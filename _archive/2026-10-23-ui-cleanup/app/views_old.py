"""Views for AutoExplainer (Django templates + HTMX). UI text is Uzbek."""
from __future__ import annotations

import re
from datetime import timedelta
from pathlib import Path, PurePosixPath

from django.conf import settings
from django.contrib import messages
from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from . import tasks
from .forms import NewProjectForm, ProjectMetaForm, ProjectSettingsForm, SceneForm
from .models import ComplianceCheck, Niche, Project, Scene, SuggestedTopic
from .services import scenes as scene_ops
from .services.image_providers import MODEL_PRESETS, preset_price, provider_status
from .services.images import needs_image, normalize_to_1080p
from .services import gemini_client
from .services import script as script_svc
from .services.topics import find_similar_projects

# Features switch on as their phase is built; templates hide buttons that can't work yet.
FEATURES = {"script": True, "voice": True, "images": True, "render": True}


def _is_htmx(request: HttpRequest) -> bool:
    return request.headers.get("HX-Request") == "true"


def _cadence_stats() -> dict:
    """Finished videos in the last 7/30 days - soft reminder against mass-production."""
    now = timezone.now()
    done = Project.objects.filter(status=Project.Status.DONE)
    return {
        "done_7": done.filter(finished_at__gte=now - timedelta(days=7)).count(),
        "done_30": done.filter(finished_at__gte=now - timedelta(days=30)).count(),
    }


# ------------------------------------------------------------------ new project
def home(request: HttpRequest) -> HttpResponse:
    """New-project form with duplicate-topic guard."""
    similar = []
    niche = Niche.active()
    initial = {}
    if niche:
        initial = {"target_minutes": niche.default_minutes, "seconds_per_image": niche.default_seconds_per_image}
    if request.method == "GET" and request.GET.get("suggestion"):
        sug = get_object_or_404(SuggestedTopic, pk=request.GET["suggestion"])
        initial.update({"topic": sug.topic_text, "source_suggestion": sug.pk})

    form = NewProjectForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        d = form.cleaned_data
        similar = find_similar_projects(d["topic"])
        if similar and not d["confirm_duplicate"]:
            messages.warning(request, "Bunga o'xshash video allaqachon bor. Baribir yaratish uchun tasdiqlash belgisini qo'ying.")
        else:
            sug = None
            if d.get("source_suggestion"):
                sug = SuggestedTopic.objects.filter(pk=d["source_suggestion"]).first()
            project = Project.objects.create(
                niche=niche,
                topic=d["topic"].strip(),
                target_duration_sec=round(d["target_minutes"] * 60),
                seconds_per_image=d["seconds_per_image"],
                tts_provider=d["tts_provider"],
                auto_approve=d["auto_approve"],
                source_suggestion=sug,
            )
            if sug:
                sug.status = SuggestedTopic.Status.USED
                sug.save(update_fields=["status"])
            messages.success(request, "Loyiha yaratildi.")
            return redirect("videos:project_detail", pk=project.pk)

    suggestions = SuggestedTopic.objects.filter(status=SuggestedTopic.Status.SUGGESTED).select_related("channel")[:12]
    recent = Project.objects.all()[:5]
    from .forms import ManualSuggestionForm

    return render(request, "videos/home.html", {"form": form, "similar": similar, "suggestions": suggestions,
                                               "niche": niche, "recent": recent,
                                               "manual_form": ManualSuggestionForm()})


def topic_check(request: HttpRequest) -> HttpResponse:
    """HTMX: live duplicate warning while typing the topic."""
    topic = request.GET.get("topic", "").strip()
    similar = find_similar_projects(topic) if len(topic) >= 4 else []
    return render(request, "videos/partials/topic_check.html", {"similar": similar})


# ------------------------------------------------------------------ list
def project_list(request: HttpRequest) -> HttpResponse:
    """Permanent video history with search and status filter."""
    qs = Project.objects.select_related("source_suggestion__channel").prefetch_related("thumbnails", "scenes")
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    if q:
        qs = qs.filter(Q(topic__icontains=q) | Q(title__icontains=q))
    if status:
        qs = qs.filter(status=status)
    ctx = {"projects": qs, "q": q, "status": status, "statuses": Project.Status.choices, **_cadence_stats()}
    return render(request, "videos/project_list.html", ctx)


# ------------------------------------------------------------------ studio
def _srt_url(project) -> str:
    """The .srt the render writes next to final.mp4 (for uploading captions to YouTube), if any."""
    if not project.final_video:
        return ""
    srt = PurePosixPath(project.final_video.name).with_suffix(".srt")
    return f"{settings.MEDIA_URL}{srt}" if (Path(settings.MEDIA_ROOT) / srt).exists() else ""


def project_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """The studio: player, metadata, scenes editor, settings."""
    project = get_object_or_404(Project.objects.select_related("music_track", "source_suggestion__channel"), pk=pk)
    images_ready, images_provider = provider_status()
    scenes = list(project.scenes.all())
    from .services import director

    ctx = {
        "direction": director.summary(project),
        "srt_url": _srt_url(project),
        "model_presets": MODEL_PRESETS,
        "model_price": preset_price(project.image_model or settings.RUNWARE_MODEL),
        "default_model_price": preset_price(settings.RUNWARE_MODEL),
        "model_known": any(m == project.image_model for m, *_ in MODEL_PRESETS),
        "prompts_text": __import__("apps.videos.services.manual_images", fromlist=["x"]).prompts_txt(project, spaced=True),
        "prompt_count": len(scenes),
        "project": project,
        "scenes": scenes,
        "images_ready": images_ready,
        "images_provider": images_provider,
        "missing_images": sum(1 for s in scenes if needs_image(s)),
        "meta_form": ProjectMetaForm(instance=project, prefix="meta"),
        "settings_form": ProjectSettingsForm(instance=project, prefix="set"),
        "features": FEATURES,
        "gemini_ok": gemini_client.is_configured(),
        "produce_ok": project.status in PRODUCE_OK and bool(scenes),
        "voiced": sum(1 for s in scenes if s.audio),
        "imaged": sum(1 for s in scenes if s.image),
        "compliance": ComplianceCheck.objects.filter(project=project).first(),
        "script": project.script_json or {},
        "word_total": sum(len(s.narration.split()) for s in scenes),
        "word_budget": script_svc.word_budget(project.target_duration_sec),
        "scene_target": script_svc.scene_count(project.target_duration_sec, project.seconds_per_image),
        "estimated_images": max(1, round(project.target_duration_sec / project.seconds_per_image)),
        "max_images": settings.MAX_IMAGES_PER_PROJECT,
    }
    return render(request, "videos/project_detail.html", ctx)


def project_status(request: HttpRequest, pk: int) -> HttpResponse:
    """HTMX partial polled every 3 s while the project is busy."""
    project = get_object_or_404(Project, pk=pk)
    was_busy = request.GET.get("poll") == "1"  # page reloads once the job finishes
    return render(request, "videos/partials/project_status.html", {"project": project, "was_busy": was_busy})


@require_POST
def project_meta_save(request: HttpRequest, pk: int) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    form = ProjectMetaForm(request.POST, instance=project, prefix="meta")
    if form.is_valid():
        form.save()
        messages.success(request, "Sarlavha, tavsif va teglar saqlandi.")
    else:
        messages.error(request, "Saqlanmadi: maydonlarni tekshiring.")
    return redirect("videos:project_detail", pk=pk)


@require_POST
def project_settings_save(request: HttpRequest, pk: int) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    form = ProjectSettingsForm(request.POST, instance=project, prefix="set")
    if form.is_valid():
        form.save()
        messages.success(request, "Sozlamalar saqlandi.")
    else:
        messages.error(request, "Sozlamalar saqlanmadi: " + "; ".join(
            f"{form.fields[f].label}: {e[0]}" for f, e in form.errors.items() if f in form.fields))
    return redirect("videos:project_detail", pk=pk)


@require_POST
def project_script_generate(request: HttpRequest, pk: int) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not gemini_client.is_configured():
        messages.error(request, ".env faylida GEMINI_API_KEY va GEMINI_TEXT_MODEL (masalan gemini-3.8-flash) bo'lishi kerak.")
    elif project.is_working:
        messages.info(request, "Bu loyiha uchun vazifa allaqachon ishlayapti.")
    else:
        if project.status == Project.Status.FAILED:
            project.set_status(Project.Status.DRAFT, "")
        tasks.enqueue("generate_script", project)
        messages.success(request, "Gemini ssenariy yozmoqda. Sahifa tayyor bo'lganda o'zi yangilanadi.")
    return redirect("videos:project_detail", pk=pk)


@require_POST
def project_script_import(request: HttpRequest, pk: int) -> HttpResponse:
    """Load a ready script (JSON written by Claude or by hand) instead of asking Gemini."""
    import json

    from pydantic import ValidationError

    project = get_object_or_404(Project, pk=pk)
    raw = ""
    if request.FILES.get("script_file"):
        raw = request.FILES["script_file"].read().decode("utf-8-sig", errors="replace")
    else:
        raw = request.POST.get("script_text", "")
    try:
        data = script_svc.ScriptOut.model_validate(json.loads(raw))
    except (ValueError, ValidationError) as exc:
        messages.error(request, f"JSON o'qilmadi: {str(exc)[:300]}")
        return redirect("videos:project_detail", pk=pk)
    if project.is_working:
        messages.info(request, "Vazifa ishlayapti, tugashini kuting.")
        return redirect("videos:project_detail", pk=pk)
    default_mood = project.niche.default_mood if project.niche else "mysterious"
    data = script_svc.clean_script(data, default_mood, script_svc.hook_scene_count_for(data.scenes))
    script_svc.save_script(project, data)
    project.set_status(Project.Status.SCRIPT_READY,
                       f"Ssenariy yuklandi: {len(data.scenes)} sahna, {script_svc.total_words(project)} so'z. Ko'rib chiqing va tasdiqlang.")
    ComplianceCheck.objects.filter(project=project).delete()
    if gemini_client.is_configured():
        Project.objects.filter(pk=pk).update(progress_message="Ssenariy yuklandi. Qoidalar tekshiruvi o'tkazilmoqda...")
        tasks.enqueue("rerun_compliance", project)
    messages.success(request, f"Ssenariy yuklandi: {len(data.scenes)} ta sahna.")
    return redirect("videos:project_detail", pk=pk)


@require_POST
def project_compliance(request: HttpRequest, pk: int) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.scenes.exists():
        messages.error(request, "Avval ssenariy kerak.")
    elif not gemini_client.is_configured():
        messages.error(request, "Tekshiruv uchun Gemini kerak.")
    elif not project.is_working:
        Project.objects.filter(pk=pk).update(progress_message="Ssenariy qoidalar bo'yicha tekshirilmoqda...")
        tasks.enqueue("rerun_compliance", project)
    return redirect("videos:project_detail", pk=pk)


@require_POST
def project_direct(request: HttpRequest, pk: int) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.scenes.exists():
        messages.error(request, "Avval ssenariy kerak.")
    elif not gemini_client.is_configured():
        messages.error(request, "Rejissyor uchun Gemini kerak (.env da GEMINI_API_KEY).")
    elif not project.is_working:
        tasks.enqueue("direct_scenes", project)
    return redirect("videos:project_detail", pk=pk)


@require_POST
def project_approve(request: HttpRequest, pk: int) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.scenes.exists():
        messages.error(request, "Tasdiqlash uchun sahnalar kerak.")
    elif project.status in (Project.Status.DRAFT, Project.Status.SCRIPT_READY, Project.Status.FAILED):
        project.set_status(Project.Status.APPROVED, "Ssenariy tasdiqlandi. Endi rasmlarni chizish mumkin; ovoz va montaj keyingi bosqichlarda.")
        messages.success(request, "Ssenariy tasdiqlandi.")
    return redirect("videos:project_detail", pk=pk)


PRODUCE_OK = {Project.Status.APPROVED, Project.Status.DONE, Project.Status.FAILED}


@require_POST
def project_produce(request: HttpRequest, pk: int) -> HttpResponse:
    """Images + voice + render in the background. quality = preview (720p, fast) | final (1080p)."""
    project = get_object_or_404(Project, pk=pk)
    quality = "preview" if request.POST.get("quality") == "preview" else "final"
    if not project.scenes.exists():
        messages.error(request, "Sahnalar yo'q.")
    elif project.status not in PRODUCE_OK:
        messages.error(request, "Avval ssenariyni tasdiqlang.")
    elif project.is_working:
        messages.info(request, "Vazifa allaqachon ishlayapti.")
    else:
        Project.objects.filter(pk=pk).update(progress_message="Navbatda...")
        tasks.enqueue("produce_video", project, quality, request.POST.get("captions", "1") != "0")
        messages.success(request, "Video yaratilmoqda. Rasmlar, ovoz va montaj bir necha daqiqa oladi — sahifa o'zi yangilanadi.")
    return redirect("videos:project_detail", pk=pk)


@require_POST
def scene_voice_generate(request: HttpRequest, pk: int) -> HttpResponse:
    scene = get_object_or_404(Scene.objects.select_related("project"), pk=pk)
    project = scene.project
    if not scene.narration.strip():
        messages.error(request, "Sahnada matn yo'q.")
    elif project.is_working:
        messages.info(request, "Boshqa vazifa ishlayapti.")
    else:
        tasks.enqueue("regenerate_scene_voice", project, scene.pk)
    return redirect("videos:project_detail", pk=project.pk)


@require_POST
def project_use_title(request: HttpRequest, pk: int) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    title = request.POST.get("title", "").strip()
    if title:
        project.title = title[:300]
        project.save(update_fields=["title", "updated_at"])
    return redirect("videos:project_detail", pk=pk)


@require_POST
def project_run_demo(request: HttpRequest, pk: int) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if project.is_working:
        messages.info(request, "Bu loyiha uchun vazifa allaqachon ishlayapti.")
    else:
        project.set_status(Project.Status.DRAFT, "Navbatda...")
        tasks.enqueue("run_demo_pipeline", project)
        messages.success(request, "Sinov vazifasi navbatga qo'yildi. `python manage.py dev` ishlab turganiga ishonch hosil qiling.")
    return redirect("videos:project_detail", pk=pk)


@require_POST
def project_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """Only I delete projects, from the UI. Files are removed along with the rows."""
    project = get_object_or_404(Project, pk=pk)
    from .services.files import delete_project_files

    delete_project_files(project)
    project.delete()
    messages.success(request, "Loyiha o'chirildi.")
    return redirect("videos:project_list")


@require_POST
def project_images_generate(request: HttpRequest, pk: int) -> HttpResponse:
    """Draw every missing scene image in the background."""
    project = get_object_or_404(Project, pk=pk)
    ready, msg = provider_status()
    if not ready:
        messages.error(request, msg)
    elif project.is_working:
        messages.info(request, "Bu loyiha uchun vazifa allaqachon ishlayapti.")
    elif request.POST.get("mode") == "hero":
        from .services.images import mentions_main_character

        ids = [s.pk for s in project.scenes.order_by("order")
               if not s.image_locked and s.image_prompt.strip() and mentions_main_character(s.image_prompt)]
        if not ids:
            messages.info(request, "Bosh qahramon ko'rinadigan (qo'lda yuklanmagan) sahna topilmadi.")
        else:
            Project.objects.filter(pk=pk).update(progress_message="Qahramonli rasmlar navbatda...")
            tasks.enqueue("generate_images", project, ids, True)
            messages.success(request, f"{len(ids)} ta qahramonli sahna yangi personaj tavsifi bilan qayta chizilmoqda.")
    else:
        Project.objects.filter(pk=pk).update(progress_message="Rasmlar navbatda...")
        tasks.enqueue("generate_images", project)
        messages.success(request, "Rasmlar fonda chizilmoqda. Sahifa tugagach o'zi yangilanadi.")
    return redirect("videos:project_detail", pk=pk)


# ------------------------------------------------------------------ hand-made images (Google Flow etc.)
def project_flow_prompts(request: HttpRequest, pk: int) -> HttpResponse:
    """All image prompts ready to paste into Google Flow (or a bulk-prompt extension)."""
    from .services import manual_images

    project = get_object_or_404(Project, pk=pk)
    fmt = request.GET.get("format")
    if fmt in ("video", "video_numbered"):
        from .services import hook_video

        resp = HttpResponse(hook_video.prompts_txt(project, numbered=fmt == "video_numbered", spaced=True),
                            content_type="text/plain; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="hook_video_promptlar_{project.pk}.txt"'
        return resp
    raw_name = request.GET.get("ism", "")
    char_name = manual_images.clean_character_name(raw_name)
    if raw_name and not char_name:
        messages.warning(request, "Personaj nomi pastki chiziqli bo'lishi kerak, masalan: main_hero")
    if fmt in ("txt", "numbered", "compact"):
        # txt / numbered: an empty line between prompts; compact: one prompt per line (bulk-prompt extensions)
        body = manual_images.prompts_txt(project, numbered=fmt == "numbered", character_name=char_name,
                                         spaced=fmt != "compact")
        resp = HttpResponse(body, content_type="text/plain; charset=utf-8")
        name = f"promptlar_{project.pk}{'_raqamli' if fmt == 'numbered' else ''}{'_zich' if fmt == 'compact' else ''}.txt"
        resp["Content-Disposition"] = f'attachment; filename="{name}"'
        return resp
    from .services import flow_queue, hook_video

    rows = manual_images.prompt_rows(project, char_name)
    scenes = {s.order: s for s in project.scenes.all()}
    hook_rows = [(o, p, scenes.get(o)) for o, p in hook_video.prompt_rows(project)]
    return render(request, "videos/flow_prompts.html", {
        "project": project,
        "hook_rows": hook_rows,
        "flow_jobs": project.flow_jobs.select_related("scene").order_by("kind", "scene__order"),
        "flow_counts": flow_queue.counts(project),
        "flow_token": settings.FLOW_API_TOKEN,
        "flow_export_dir": flow_queue.export_dir(project),
        "hook_done": sum(1 for _, _, s in hook_rows if s and s.video),
        "hook_text": hook_video.prompts_txt(project, spaced=True),
        "char_name": char_name,
        "rows": [(o, p, scenes.get(o)) for o, p in rows],
        "all_text": manual_images.prompts_txt(project, character_name=char_name, spaced=True),
        "done": sum(1 for s in scenes.values() if s.image),
    })


@require_POST
def project_images_upload(request: HttpRequest, pk: int) -> HttpResponse:
    """Bulk upload: every file goes to its scene (number in the name / prompt text / selection order)."""
    from .services import manual_images

    project = get_object_or_404(Project, pk=pk)
    files = request.FILES.getlist("images")
    back = "videos:project_flow_prompts" if request.POST.get("next") == "prompts" else "videos:project_detail"
    if not files:
        messages.error(request, "Rasm tanlanmadi.")
        return redirect(back, pk=pk)
    if project.is_working:
        messages.info(request, "Loyihada hozir boshqa vazifa ishlayapti — tugagach qayta yuklang.")
        return redirect(back, pk=pk)
    mode = "order" if request.POST.get("mode") == "order" else "auto"
    try:
        start = max(1, int(request.POST.get("start") or 1))
    except ValueError:
        start = 1
    scenes = list(project.scenes.all())
    by_name = {f.name: f for f in files}
    result = manual_images.match_files(list(by_name), scenes, mode=mode, start=start)
    by_order = {s.order: s for s in scenes}
    saved, broken = 0, []
    for name, order in sorted(result.assigned.items(), key=lambda kv: kv[1]):
        try:
            manual_images.save_uploaded(by_order[order], by_name[name])
            saved += 1
        except Exception:  # noqa: BLE001 - a broken file must not stop the others
            broken.append(name)
    if saved:
        Project.objects.filter(pk=pk).update(has_unrendered_changes=True)
        messages.success(request, f"{saved} ta rasm sahnalarga joylandi.")
    problems = result.unmatched + broken
    if problems:
        hint = ("Fayl nomiga sahna raqamini yozing (masalan 007.png) yoki 'Tanlangan tartibda' rejimini tanlang."
                if mode == "auto" else "Rasmlar sahnalardan ko'p edi.")
        messages.warning(request, f"{len(problems)} ta fayl joylanmadi: {', '.join(problems[:8])}"
                                  f"{' …' if len(problems) > 8 else ''}. {hint}")
    if result.skipped:
        messages.warning(request, f"Rasm bo'lmagan fayllar o'tkazib yuborildi: {', '.join(result.skipped[:5])}")
    return redirect(back, pk=pk)


@require_POST
def project_hook_videos_upload(request: HttpRequest, pk: int) -> HttpResponse:
    """Bulk upload of Flow/Veo clips for the hook scenes."""
    from .services import hook_video

    project = get_object_or_404(Project, pk=pk)
    files = request.FILES.getlist("videos")
    back = "videos:project_flow_prompts"
    if not files:
        messages.error(request, "Video tanlanmadi.")
        return redirect(back, pk=pk)
    if project.is_working:
        messages.info(request, "Loyihada hozir boshqa vazifa ishlayapti — tugagach qayta yuklang.")
        return redirect(back, pk=pk)
    mode = "order" if request.POST.get("mode") == "order" else "auto"
    try:
        start = max(1, int(request.POST.get("start") or 1))
    except ValueError:
        start = 1
    scenes = list(project.scenes.all())
    by_name = {f.name: f for f in files}
    result = hook_video.match_files(list(by_name), scenes, mode=mode, start=start)
    by_order = {s.order: s for s in scenes}
    saved, broken = 0, []
    for name, order in sorted(result.assigned.items(), key=lambda kv: kv[1]):
        try:
            hook_video.save_uploaded(by_order[order], by_name[name])
            saved += 1
        except Exception:  # noqa: BLE001 - one broken file must not stop the others
            broken.append(name)
    if saved:
        Project.objects.filter(pk=pk).update(has_unrendered_changes=True)
        messages.success(request, f"{saved} ta hook videosi sahnalarga joylandi.")
    problems = result.unmatched + broken
    if problems:
        messages.warning(request, f"{len(problems)} ta fayl joylanmadi: {', '.join(problems[:8])}. "
                                  "Fayl nomiga hook sahnasining raqamini yozing (masalan 003.mp4).")
    if result.skipped:
        messages.warning(request, f"Video bo'lmagan fayllar o'tkazib yuborildi: {', '.join(result.skipped[:5])}")
    return redirect(back, pk=pk)


@require_POST
def scene_image_generate(request: HttpRequest, pk: int) -> HttpResponse:
    """(Re)draw one scene image in the background."""
    scene = get_object_or_404(Scene.objects.select_related("project"), pk=pk)
    project = scene.project
    ready, msg = provider_status()
    if not ready:
        messages.error(request, msg)
    elif scene.image_locked:
        messages.info(request, "Bu sahnada o'zingiz yuklagan rasm bor — avval uni tahrirlashda olib tashlang.")
    elif not scene.image_prompt.strip():
        messages.error(request, f"{scene.order}-sahnada rasm tavsifi yo'q.")
    elif project.is_working:
        messages.info(request, "Boshqa vazifa ishlayapti, u tugashini kuting.")
    else:
        Project.objects.filter(pk=project.pk).update(progress_message=f"{scene.order}-sahna rasmi navbatda...")
        tasks.enqueue("generate_images", project, [scene.pk], True)
    return redirect("videos:project_detail", pk=project.pk)


# ------------------------------------------------------------------ scenes (HTMX)
def _scene_list_response(request: HttpRequest, project: Project) -> HttpResponse:
    project.refresh_from_db()
    return render(request, "videos/partials/scene_list.html", {"project": project, "scenes": project.scenes.all()})


def scene_row(request: HttpRequest, pk: int) -> HttpResponse:
    """Read-only row (used by 'Bekor qilish' in the inline editor)."""
    scene = get_object_or_404(Scene, pk=pk)
    return render(request, "videos/partials/scene_row.html", {"scene": scene, "project": scene.project})


def scene_edit(request: HttpRequest, pk: int) -> HttpResponse:
    """GET: inline edit form. POST: save and return the updated row."""
    scene = get_object_or_404(Scene.objects.select_related("project"), pk=pk)
    if request.method == "POST":
        form = SceneForm(request.POST, request.FILES, instance=scene)
        if form.is_valid():
            changed = set(form.changed_data) - {"new_image", "unlock_image"}
            if any(c.startswith("sfx") for c in changed):  # the sfxN_* rows make up Scene.sfx
                changed = {c for c in changed if not c.startswith("sfx")} | {"sfx"}
            scene = form.save(commit=False)
            upload = form.cleaned_data.get("new_image")
            if upload:
                if scene.image:
                    scene.image.delete(save=False)
                scene.image.save("scene.png", ContentFile(normalize_to_1080p(upload)), save=False)
                scene.image_locked = True
                changed.add("image")
            elif form.cleaned_data.get("unlock_image") and scene.image_locked:
                if scene.image:
                    scene.image.delete(save=False)
                scene.image = ""
                scene.image_locked = False
                changed.add("image")
            scene_ops.apply_scene_edit(scene, changed)
            return render(request, "videos/partials/scene_row.html",
                          {"scene": scene, "project": scene.project, "saved": True})
    else:
        form = SceneForm(instance=scene)
    return render(request, "videos/partials/scene_form.html", {"scene": scene, "form": form})


@require_POST
def scene_add(request: HttpRequest, pk: int) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    after = request.POST.get("after")
    scene_ops.add_scene(project, after_order=int(after) if after else None,
                        narration="", beat_type=Scene.BeatType.NORMAL)
    return _scene_list_response(request, project)


@require_POST
def scene_move(request: HttpRequest, pk: int, direction: str) -> HttpResponse:
    scene = get_object_or_404(Scene.objects.select_related("project"), pk=pk)
    scene_ops.move_scene(scene, -1 if direction == "up" else 1)
    return _scene_list_response(request, scene.project)


@require_POST
def scene_delete(request: HttpRequest, pk: int) -> HttpResponse:
    scene = get_object_or_404(Scene.objects.select_related("project"), pk=pk)
    project = scene.project
    scene_ops.delete_scene(scene)
    return _scene_list_response(request, project)


@require_POST
def project_image_model(request: HttpRequest, pk: int) -> HttpResponse:
    """Choose which Runware model draws this project's pictures (before generating them)."""
    project = get_object_or_404(Project, pk=pk)
    choice = (request.POST.get("custom") or request.POST.get("model") or "").strip()
    if choice and not (re.fullmatch(r"[\w.\-]+:[\w.\-]+@[\w.\-]+", choice) or re.fullmatch(r"[\w.\-]+/[\w.\-]+", choice)):
        messages.error(request, "Model ID noto'g'ri. Runware: ideogram:4.5@0, Replicate: black-forest-labs/flux-schnell")
        return redirect("videos:project_detail", pk=pk)
    project.image_model = choice
    project.save(update_fields=["image_model", "updated_at"])
    price = preset_price(choice or settings.RUNWARE_MODEL)
    est = f" (taxminiy narx: ${price * max(1, project.scenes.count()):.2f} butun video uchun)" if price else ""
    messages.success(request, f"Rasm modeli: {choice or 'standart (.env)'}{est}")
    return redirect("videos:project_detail", pk=pk)
