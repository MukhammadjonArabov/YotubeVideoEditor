"""Background jobs run by django-q2 (`python manage.py qcluster`).

Phase 1 only contains a *demo* pipeline that walks through the statuses with
sleeps, to prove that the worker, the ORM broker and live status polling work.
Real steps replace it phase by phase.
"""
from __future__ import annotations

import logging
import time
import traceback

from django_q.tasks import async_task

from .models import Project

logger = logging.getLogger(__name__)

DEMO_STEP_SECONDS = 3


def enqueue(func_name: str, project: Project, *args) -> str:
    """Queue `apps.videos.tasks.<func_name>(project.id, *args)` and flag the project as working."""
    Project.objects.filter(pk=project.pk).update(is_working=True, error_message="")
    return async_task(f"apps.videos.tasks.{func_name}", project.pk, *args, task_name=f"{func_name}-p{project.pk}")


def run_demo_pipeline(project_id: int) -> None:
    """Fake pipeline: script_ready -> approved -> generating_assets -> rendering -> done."""
    project = Project.objects.get(pk=project_id)
    logger.info("Demo pipeline started for project %s", project_id)
    try:
        steps = [
            (Project.Status.SCRIPT_READY, "Sinov: ssenariy yozilayotgandek..."),
            (Project.Status.APPROVED, "Sinov: ssenariy tasdiqlangandek..."),
            (Project.Status.GENERATING_ASSETS, "Sinov: rasm va ovoz yaratilayotgandek..."),
            (Project.Status.RENDERING, "Sinov: ffmpeg bilan montaj qilinayotgandek..."),
        ]
        for status, message in steps:
            project.set_status(status, message)
            time.sleep(DEMO_STEP_SECONDS)
        project.set_status(Project.Status.DONE, "Sinov tugadi. Haqiqiy jarayon keyingi bosqichlarda qo'shiladi.")
    except Exception as exc:  # noqa: BLE001 - we want every failure recorded on the project
        logger.exception("Demo pipeline failed for project %s", project_id)
        project.error_message = f"{exc}\n\n{traceback.format_exc()}"
        project.save(update_fields=["error_message"])
        project.set_status(Project.Status.FAILED, "Xato yuz berdi")
    finally:
        Project.objects.filter(pk=project_id).update(is_working=False)


def generate_images(project_id: int, scene_ids: list[int] | None = None, force: bool = False) -> None:
    """Draw scene images, IMAGE_CONCURRENCY at a time.

    scene_ids=None -> every scene that is missing an image. A failing scene is marked
    'failed' with the reason and the rest continue, so you can retry it later.
    """
    import random

    from django.conf import settings

    from .services import assets
    from .services.image_providers import apply_model, get_provider
    from .services.images import needs_image

    project = Project.objects.get(pk=project_id)

    def progress(msg: str) -> None:
        Project.objects.filter(pk=project_id).update(progress_message=msg)

    try:
        provider = apply_model(get_provider(), project.image_model)
        scenes = list(project.scenes.order_by("order"))
        if scene_ids is not None:
            wanted = set(scene_ids)
            scenes = [s for s in scenes if s.pk in wanted and not s.image_locked and s.image_prompt.strip()]
            if not force:
                scenes = [s for s in scenes if not s.image]
        else:
            scenes = [s for s in scenes if needs_image(s)]
        cap = settings.MAX_IMAGES_PER_PROJECT
        existing = project.scenes.exclude(image="").count()
        if scene_ids is None and existing + len(scenes) > cap:
            scenes = scenes[: max(0, cap - existing)]
        salt_fn = (lambda: random.randint(1, 10_000)) if force else None
        rep = assets.produce(scenes, [], provider, None, progress, salt_fn=salt_fn)
        cost = _add_image_cost(project_id, provider)
        msg = f"Rasmlar: {rep.images_done} ta tayyor" + (f" · ${cost:.3f} sarflandi" if cost else "")
        if getattr(provider, "notice", ""):
            msg += f" ({provider.notice})"
        if rep.images_flagged:
            msg += f", {rep.images_flagged} tasida qahramon hali ham farq qilishi mumkin (⚠️ belgili sahnalar)"
        if rep.images_failed:
            msg += f", {rep.images_failed} ta xato (sahnalarda sababini ko'ring)"
        if rep.images_skipped:
            msg += f", {rep.images_skipped} tasi limit tufayli chizilmadi"
        Project.objects.filter(pk=project_id).update(progress_message=msg, has_unrendered_changes=True)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Image job failed for project %s", project_id)
        Project.objects.filter(pk=project_id).update(progress_message=f"Rasm chizish to'xtadi: {exc}")
    finally:
        Project.objects.filter(pk=project_id).update(is_working=False)


# ------------------------------------------------------------------ channels
def channel_research(channel_id: int, suggest: bool = True) -> None:
    """Import a reference channel from YouTube, analyse its style with Gemini, suggest topics."""
    from .models import ChannelSource
    from .services import channel_research as cr
    from .services import gemini_client

    ch = ChannelSource.objects.get(pk=channel_id)

    def step(msg: str) -> None:
        ChannelSource.objects.filter(pk=channel_id).update(progress_message=msg)

    try:
        step("YouTube'dan kanal va videolar olinmoqda...")
        n = cr.import_channel(ch)
        ch.refresh_from_db()
        if not gemini_client.is_configured():
            ChannelSource.objects.filter(pk=channel_id).update(
                state=ChannelSource.State.READY, error_message="",
                progress_message=f"{n} ta video olindi. Tahlil va takliflar uchun .env da GEMINI_API_KEY kerak.")
            return
        step(f"{n} ta video olindi. Gemini uslubni tahlil qilmoqda...")
        cr.analyze_style(ch)
        msg = f"{n} ta video tahlil qilindi."
        if suggest:
            step("Yangi mavzular o'ylab topilmoqda...")
            created = cr.suggest_topics(ch)
            msg += f" {len(created)} ta yangi mavzu taklif qilindi."
        ChannelSource.objects.filter(pk=channel_id).update(state=ChannelSource.State.READY, progress_message=msg, error_message="")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Channel research failed for %s", channel_id)
        ChannelSource.objects.filter(pk=channel_id).update(
            state=ChannelSource.State.FAILED, progress_message="Xato", error_message=str(exc)[:2000])


def channel_suggest_more(channel_id: int) -> None:
    from .models import ChannelSource
    from .services import channel_research as cr

    try:
        ch = ChannelSource.objects.get(pk=channel_id)
        created = cr.suggest_topics(ch)
        ChannelSource.objects.filter(pk=channel_id).update(
            state=ChannelSource.State.READY, progress_message=f"{len(created)} ta yangi mavzu qo'shildi.", error_message="")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Suggestions failed for %s", channel_id)
        ChannelSource.objects.filter(pk=channel_id).update(
            state=ChannelSource.State.FAILED, progress_message="Xato", error_message=str(exc)[:2000])


# ------------------------------------------------------------------ policy watch
def policy_check_all() -> dict:
    """Scheduled every POLICY_CHECK_INTERVAL_DAYS days (and on the 'check now' button)."""
    from .services import policy_watch

    return policy_watch.check_all()


def policy_check_one(doc_id: int) -> str:
    from .models import PolicyDocument
    from .services import policy_watch

    return policy_watch.check_document(PolicyDocument.objects.get(pk=doc_id))


# ------------------------------------------------------------------ script (phase 2)
def generate_script(project_id: int) -> None:
    """Gemini writes the script -> scenes are saved -> compliance check -> stop for review
    (or auto-approve when enabled and the check did not fail)."""
    from .services import compliance, script

    project = Project.objects.get(pk=project_id)
    try:
        Project.objects.filter(pk=project_id).update(progress_message="Gemini ssenariy yozmoqda (30-90 soniya)...")
        data = script.generate(project)
        project.refresh_from_db()
        script.save_script(project, data)
        project.set_status(Project.Status.SCRIPT_READY,
                           f"Ssenariy tayyor: {len(data.scenes)} sahna, {script.total_words(project)} so'z. "
                           "Rejissyor sahnalarni belgilamoqda...")
        _run_director(project)
        _run_compliance(project, compliance)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Script generation failed for project %s", project_id)
        Project.objects.filter(pk=project_id).update(error_message=str(exc)[:4000])
        project.refresh_from_db()
        project.set_status(Project.Status.FAILED if not project.scenes.exists() else project.status,
                           f"Ssenariy yozilmadi: {str(exc)[:200]}")
    finally:
        Project.objects.filter(pk=project_id).update(is_working=False)


def _run_director(project) -> str:
    """Emotion / camera / SFX / music marks for every scene. Never fails the job."""
    from django.conf import settings

    from .services import director

    if not getattr(settings, "DIRECTOR_ENABLED", True):
        return ""
    try:
        changed = director.apply(project, director.direct(project))
        return f"Rejissyor {changed} ta sahnani belgiladi."
    except Exception as exc:  # noqa: BLE001
        logger.warning("Director failed for project %s: %s", project.pk, exc)
        return f"Rejissyor ishlamadi: {str(exc)[:150]}"


def direct_scenes(project_id: int) -> None:
    """The "🎬 Rejissyor" button: re-mark every scene (overwrites hand edits of these fields)."""
    project = Project.objects.get(pk=project_id)
    try:
        Project.objects.filter(pk=project_id).update(progress_message="Rejissyor sahnalarni belgilamoqda (20-60 s)...")
        Project.objects.filter(pk=project_id).update(progress_message=_run_director(project))
    finally:
        Project.objects.filter(pk=project_id).update(is_working=False)


def _run_compliance(project, compliance) -> None:
    try:
        check = compliance.run_check(project)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Compliance check failed for %s: %s", project.pk, exc)
        project.set_status(project.status, f"Ssenariy tayyor, lekin tekshiruv o'tmadi: {str(exc)[:150]}. Qayta tekshiring.")
        return
    labels = {"pass": "✅ tekshiruvdan o'tdi", "warning": "⚠️ ogohlantirishlar bor", "fail": "❌ jiddiy muammo bor"}
    if project.auto_approve and compliance.can_auto_approve(check.status):
        project.set_status(Project.Status.APPROVED, f"Avtomatik tasdiqlandi ({labels[check.status]}).")
    else:
        project.set_status(Project.Status.SCRIPT_READY, f"Ssenariy tayyor — {labels[check.status]}. Ko'rib chiqing va tasdiqlang.")


def rerun_compliance(project_id: int) -> None:
    from .services import compliance

    project = Project.objects.get(pk=project_id)
    try:
        _run_compliance(project, compliance)
    finally:
        Project.objects.filter(pk=project_id).update(is_working=False)


# ------------------------------------------------------------------ voice + render (phases 3-4)
VOICE_PAUSE_SEC = 30
VOICE_MAX_PAUSES = 4  # up to ~2 minutes of waiting for the connection to come back


def _voice_second_chance(failed_scenes, provider, progress) -> list[int]:
    """Voice-overs that failed in the parallel pass (usually a dropped connection): wait, then retry
    one by one. Stops after 3 failures in a row. Returns orders of scenes whose voice still failed."""
    from .models import Scene
    from .services.tts import TTSError
    from .services.voice import generate_scene_audio

    if not failed_scenes:
        return []
    progress(f"{len(failed_scenes)} ta ovoz yaratilmadi — {VOICE_PAUSE_SEC} s kutib qayta urinilmoqda...")
    time.sleep(VOICE_PAUSE_SEC)
    failed = []
    streak = 0
    pauses = 1
    for i, scene in enumerate(failed_scenes, start=1):
        retries = 0
        while True:
            progress(f"Ovoz qayta yaratilmoqda: {i}/{len(failed_scenes)} ({scene.order}-sahna)")
            try:
                generate_scene_audio(scene, provider=provider, force=True)
                streak = 0
                break
            except TTSError as exc:
                if retries < 2 and pauses < VOICE_MAX_PAUSES:
                    retries += 1
                    pauses += 1
                    progress(f"Ovoz xizmatiga ulanib bo'lmadi — {VOICE_PAUSE_SEC} s kutib qayta urinilmoqda "
                             f"({pauses}/{VOICE_MAX_PAUSES}, {scene.order}-sahna)")
                    time.sleep(VOICE_PAUSE_SEC)
                    continue
                streak += 1
                failed.append(scene.order)
                Scene.objects.filter(pk=scene.pk).update(status=Scene.Status.FAILED, error_message=str(exc))
                break
        if streak >= 3:
            failed += [s.order for s in failed_scenes[i:]]  # still offline after waiting - stop, keep what is done
            break
    return failed


def _add_image_cost(project_id: int, provider) -> float:
    """Add what the provider spent in this job to the project's running total. Returns this job's cost."""
    from django.db.models import F

    from .services.image_providers import spent

    cost, n = spent(provider)
    if n:
        Project.objects.filter(pk=project_id).update(image_cost=F("image_cost") + cost,
                                                     image_cost_count=F("image_cost_count") + n)
    return cost


def _elevenlabs_usable(provider) -> bool:
    """A 5-character test line before the big job: a wrong key or an empty balance shows up here, not after
    half of the video is voiced. A dropped connection gets one more try."""
    import tempfile
    from pathlib import Path

    from .services.tts import TTSError

    for attempt in (1, 2):
        try:
            with tempfile.TemporaryDirectory() as tmp:
                provider.synthesize("Test.", Path(tmp) / "probe.mp3")
            return True
        except TTSError as exc:
            logger.warning("ElevenLabs probe failed (%s): %s", attempt, str(exc)[:160])
            time.sleep(3)
    return False


def _voice_all_with_edge(project, progress) -> list[int]:
    """ElevenLabs is out (key, balance, outage): voice EVERY line again with the free Edge TTS, so the whole video
    keeps one voice. The project is switched to Edge, so later edits sound the same."""
    from .services import assets
    from .services.tts import get_tts

    edge = get_tts("edge", project)
    Project.objects.filter(pk=project.pk).update(tts_provider="edge")
    project.tts_provider = "edge"
    scenes = [s for s in project.scenes.order_by("order") if s.narration.strip()]
    progress("ElevenLabs ishlamadi — hamma ovoz bepul Edge TTS bilan yaratilmoqda...")
    rep = assets.produce([], scenes, None, edge, progress)
    return _voice_second_chance([s for s, _ in rep.voice_failed], edge, progress)


def _generate_assets(project, progress, images: bool = True, voice: bool = True) -> tuple[str, list[int]]:
    """Missing images and voice-overs, made at the same time. Returns (note for the user, failed voice orders)."""
    from .services import assets
    from .services.image_providers import ImageProviderNotConfigured, apply_model, get_provider
    from .services.images import needs_image
    from .services.tts import get_tts
    from .services.voice import needs_audio

    scenes = list(project.scenes.order_by("order"))
    from .services import flow_queue

    waiting = flow_queue.scenes_waiting_for_flow(project)  # their pictures come from the Flow extension
    img_todo = [s for s in scenes if needs_image(s) and s.pk not in waiting] if images else []
    voice_todo = [s for s in scenes if needs_audio(s)] if voice else []
    from .services.tts import navoiy

    if voice_todo and project.niche and navoiy.is_navoiy(project.niche.tts_voice):  # local cloned voice, one batch
        failed = navoiy.voice_scenes(project, voice_todo, progress)
        if failed:
            return "", failed
        voice_todo = []
    note = ""
    image_provider = None
    if img_todo:
        try:
            image_provider = apply_model(get_provider(), project.image_model)
        except ImageProviderNotConfigured as exc:
            note = f"Rasm provayderi sozlanmagan ({exc}) — rangli kartochkalar ishlatildi."
            img_todo = []
    tts = get_tts(project.tts_provider, project) if voice_todo else None
    voice_note = ""
    if tts is not None and tts.name == "elevenlabs" and not _elevenlabs_usable(tts):
        voice_todo = [s for s in scenes if s.narration.strip()]  # all lines again, in the fallback voice
        for s in voice_todo:
            if s.audio:
                s.audio.delete(save=False)
                s.audio = ""
        tts = get_tts("edge", project)
        Project.objects.filter(pk=project.pk).update(tts_provider="edge")
        project.tts_provider = "edge"
        voice_note = "ElevenLabs ishlamadi (kalit yoki balans) — ovoz bepul Edge TTS bilan yaratildi."
    if not img_todo and not voice_todo:
        return note, []
    rep = assets.produce(img_todo, voice_todo, image_provider, tts, progress)
    cost = _add_image_cost(project.pk, image_provider)
    if cost:
        note = (note + f" Rasmlarga ${cost:.3f} sarflandi.").strip()
    failed_voice = _voice_second_chance([s for s, _ in rep.voice_failed], tts, progress)
    if failed_voice and tts is not None and tts.name == "elevenlabs":  # ran out part-way through
        failed_voice = _voice_all_with_edge(project, progress)
        voice_note = "ElevenLabs yarim yo'lda to'xtadi — butun ovoz bepul Edge TTS bilan qayta yaratildi."
    notice = getattr(image_provider, "notice", "") if image_provider else ""
    if rep.image_quota_hit:
        note = (f"Rasm limiti tugadi — {rep.images_failed + rep.images_skipped} ta sahnada rangli kartochka "
                f"ishlatildi. {notice}").strip()
    elif rep.images_failed:
        note = f"{rep.images_failed} ta rasm chizilmadi — ularda rangli kartochka ishlatildi. {notice}".strip()
    elif notice:
        note = notice
    return " ".join(x for x in (voice_note, note) if x), failed_voice


def _generate_missing_voice(project, progress) -> list[int]:
    """Returns orders of scenes whose voice failed."""
    return _generate_assets(project, progress, images=False)[1]


def produce_video(project_id: int, quality: str = "final", captions: bool = False) -> None:
    """Approved script -> missing images -> missing voice -> render -> MP4 (the whole pipeline)."""
    from django.conf import settings

    from .services import render

    project = Project.objects.get(pk=project_id)

    def progress(msg: str) -> None:
        Project.objects.filter(pk=project_id).update(progress_message=msg)

    try:
        project.set_status(Project.Status.GENERATING_ASSETS, "Rasm va ovoz tayyorlanmoqda...")
        note, failed_voice = _generate_assets(project, progress)
        if failed_voice:
            raise render.RenderError(f"Ovoz yaratilmadi ({len(failed_voice)} ta sahna: {failed_voice[:15]}). "
                                     "Tayyor ovozlar saqlandi — qayta bosganingizda faqat qolganlari yaratiladi. "
                                     "Internetni tekshiring yoki ovoz provayderini almashtiring, keyin qayta bosing.")
        from .services.images import needs_image

        no_image = [s.order for s in project.scenes.order_by("order") if needs_image(s)]
        if no_image:  # a render would cache placeholder pictures, so stop here instead
            raise render.RenderError(f"Rasm chizilmadi ({len(no_image)} ta sahna: {no_image[:15]}). Odatda rasm provayderining "
                                     "kunlik bepul limiti tugagan. Tayyor ovoz va rasmlar saqlandi; limit yangilangach "
                                     "'Video yaratish' ni qayta bossangiz faqat qolganlari yaratiladi.")
        project.set_status(Project.Status.RENDERING, "Montaj boshlandi...")
        out, total = render.render_project(project, quality=quality, progress=progress, captions=captions)
        rel = out.relative_to(settings.MEDIA_ROOT).as_posix()
        project.refresh_from_db()
        if quality == "final":
            project.final_video.name = rel
            project.has_unrendered_changes = False
        else:
            project.preview_video.name = rel
        project.actual_duration_sec = total
        project.error_message = ""
        project.save(update_fields=["final_video", "preview_video", "has_unrendered_changes", "actual_duration_sec",
                                    "error_message", "updated_at"])
        mins = f"{int(total // 60)}:{int(total % 60):02d}"
        if quality == "final":
            project.set_status(Project.Status.DONE, f"🎉 Video tayyor ({mins}). {note}".strip())
            try:
                from .services import monetization
                monetization.check_project(project)
            except Exception:  # noqa: BLE001  the check must never fail a finished render
                logger.exception("Monetization check failed for project %s", project_id)
            from .services import dub
            if getattr(settings, "DUB_AUTO", True) and dub.wants_dub(project):
                res = dub.make_all(project, progress)  # ru / es / fr audio + translated titles; never fails the video
                bad = {k: v for k, v in res.items() if v != "ok"}
                Project.objects.filter(pk=project_id).update(progress_message=(
                    f"🎉 Video tayyor ({mins}). Dublyaj: " + ", ".join(f"{k} {'✓' if v == 'ok' else '✗'}" for k, v in res.items())))
                if bad:
                    logger.warning("Dub failed for project %s: %s", project_id, bad)
        else:
            project.set_status(Project.Status.APPROVED, f"👀 Ko'rish uchun 720p video tayyor ({mins}). {note}".strip())
    except Exception as exc:  # noqa: BLE001
        logger.exception("Video production failed for project %s", project_id)
        Project.objects.filter(pk=project_id).update(error_message=str(exc)[:8000])
        project.set_status(Project.Status.FAILED, f"To'xtadi: {str(exc).splitlines()[0][:200]}")
    finally:
        Project.objects.filter(pk=project_id).update(is_working=False)


def regenerate_scene_voice(project_id: int, scene_id: int) -> None:
    from .models import Scene
    from .services.tts import TTSError
    from .services.voice import generate_scene_audio

    scene = Scene.objects.select_related("project").get(pk=scene_id)
    try:
        Project.objects.filter(pk=project_id).update(progress_message=f"{scene.order}-sahna ovozi yaratilmoqda...")
        generate_scene_audio(scene, force=True)
        Project.objects.filter(pk=project_id).update(progress_message=f"{scene.order}-sahna ovozi tayyor.",
                                                     has_unrendered_changes=True)
    except TTSError as exc:
        Scene.objects.filter(pk=scene_id).update(status=Scene.Status.FAILED, error_message=str(exc))
        Project.objects.filter(pk=project_id).update(progress_message=f"Ovoz xatosi: {exc}")
    finally:
        Project.objects.filter(pk=project_id).update(is_working=False)
