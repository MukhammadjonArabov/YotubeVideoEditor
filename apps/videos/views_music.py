"""Music section of the site (niche kind "music"): relaxing long videos made from one looped track and looped clips.

The owner works here: edits the music prompt, listens to the takes, sets the video length, edits the Flow prompts,
uploads the clips made in Google Flow and starts the montage. Claude prepares prompts, checks quality and the publish kit
with `manage.py music_new` / `music_qc`.
"""
from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from . import music_tasks
from .models import MusicClip, MusicTake, MusicVideo, Niche
from .services import media_library, monetization, music_qc
from .services import music_video as mvs

VIDEO_EXT = {".mp4", ".mov", ".webm", ".m4v"}
AUDIO_EXT = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"}
MAX_CLIPS = 6
MAX_TAKES_PER_RUN = 3


def _int(value, default: int, lo: int, hi: int) -> int:
    try:
        return max(lo, min(hi, int(value)))
    except (TypeError, ValueError):
        return default


def _music_niche() -> Niche | None:
    return Niche.objects.filter(kind="music").order_by("id").first()


def _mmss(seconds: float | None) -> str:
    s = int(seconds or 0)
    return f"{s // 60}:{s % 60:02d}"


def niche_page(request: HttpRequest, niche: Niche) -> HttpResponse:
    """The music niche page: statistics and the list of music videos."""
    items = list(MusicVideo.objects.filter(niche=niche).prefetch_related("clips", "takes"))
    done = [m for m in items if m.status == MusicVideo.Status.DONE]
    total_sec = sum(m.actual_duration_sec or 0 for m in done)
    stats = [("Tayyor videolar", len(done), "ta"), ("Jami davomiylik", _mmss(total_sec), "daqiqa"),
             ("Jarayonda", sum(1 for m in items if m.is_working or m.status in ("music_ready", "rendering", "draft")), "ta"),
             ("Musiqa variantlari", sum(m.takes.count() for m in items), "ta")]
    return render(request, "videos/music_niche.html", {"niche": niche, "items": items, "stats": stats,
                                                       "refresh": any(m.is_working for m in items)})


def music_list(request: HttpRequest) -> HttpResponse:
    niche = _music_niche()
    return redirect("videos:niche", slug=(niche.slug or f"nisha-{niche.pk}")) if niche else redirect("videos:home")


@require_POST
def music_create(request: HttpRequest) -> HttpResponse:
    title = (request.POST.get("title") or "").strip() or "Tinchlantiruvchi tabiat musiqasi"
    mv = MusicVideo.objects.create(title=title[:200], music_prompt=mvs.DEFAULT_MUSIC_PROMPT, niche=_music_niche(),
                                   flow_prompts=[{"title": f"Klip {i}", "prompt": t} for i, t in enumerate(mvs.FLOW_CLIP_PROMPTS, 1)])
    return redirect("videos:music_detail", pk=mv.pk)


def _loop_preview_url(mv: MusicVideo) -> str:
    path = Path(settings.MEDIA_ROOT) / "music" / f"m{mv.pk}" / "loop_preview.mp3"
    return f"{settings.MEDIA_URL}music/m{mv.pk}/loop_preview.mp3?v={int(path.stat().st_mtime)}" if path.exists() else ""


def music_detail(request: HttpRequest, pk: int) -> HttpResponse:
    mv = get_object_or_404(MusicVideo, pk=pk)
    takes = list(mv.takes.all())
    selected = next((t for t in takes if t.is_selected), None)
    total_sec = mv.target_minutes * 60
    loop = mvs.loop_plan(mv.music_duration, total_sec) if mv.music_duration else None
    ctas = len(mvs.plan_ctas(total_sec, mv.cta_every_min, mv.add_subscribe, mv.add_like))
    kit = mv.kit or {}
    return render(request, "videos/music_detail.html", {
        "mv": mv, "niche": mv.niche, "takes": takes, "selected": selected, "clips": list(mv.clips.all()), "max_clips": MAX_CLIPS,
        "flow_prompts": mv.flow_prompts or [], "loop": loop, "ctas": ctas,
        "can_render": bool(mv.music_file) and mv.clips.exists() and not mv.is_working,
        "preview_url": _loop_preview_url(mv), "kit": kit, "titles": kit.get("titles", []),
        "tags_text": ", ".join(kit.get("tags", [])), "final_min": _mmss(mv.actual_duration_sec) if mv.actual_duration_sec else "",
        "refresh": mv.is_working, "vocal_clause": mvs.VOCALS_CLAUSE,
        "mon": monetization.last_report("music", mv.pk),
    })


@require_POST
def music_save(request: HttpRequest, pk: int) -> HttpResponse:
    mv = get_object_or_404(MusicVideo, pk=pk)
    p = request.POST
    mv.title = (p.get("title") or mv.title).strip()[:200]
    mv.music_prompt = (p.get("music_prompt") or "").strip()
    mv.music_seconds = _int(p.get("music_seconds"), mv.music_seconds, 60, 300)
    mv.target_minutes = _int(p.get("target_minutes"), mv.target_minutes, 5, 180)
    mv.cta_every_min = _int(p.get("cta_every_min"), mv.cta_every_min, 1, 60)
    mv.vocals = p.get("vocals") == "on"
    mv.add_subscribe = p.get("add_subscribe") == "on"
    mv.add_like = p.get("add_like") == "on"
    mv.save()
    messages.success(request, "Saqlandi.")
    return redirect("videos:music_detail", pk=pk)


@require_POST
def music_flow_save(request: HttpRequest, pk: int) -> HttpResponse:
    """Edit the Flow prompts (one textarea each; an empty one is removed)."""
    mv = get_object_or_404(MusicVideo, pk=pk)
    prompts = []
    for i in range(1, 12):
        text = (request.POST.get(f"flow{i}") or "").strip()
        if text:
            prompts.append({"title": (request.POST.get(f"flowtitle{i}") or f"Klip {len(prompts) + 1}").strip()[:80], "prompt": text})
    new = (request.POST.get("flow_new") or "").strip()
    if new:
        prompts.append({"title": f"Klip {len(prompts) + 1}", "prompt": new})
    mv.flow_prompts = prompts
    mv.save(update_fields=["flow_prompts", "updated_at"])
    messages.success(request, "Flow promptlari saqlandi.")
    return redirect("videos:music_detail", pk=pk)


@require_POST
def music_generate(request: HttpRequest, pk: int) -> HttpResponse:
    mv = get_object_or_404(MusicVideo, pk=pk)
    count = _int(request.POST.get("count"), 1, 1, MAX_TAKES_PER_RUN)
    if mv.is_working:
        messages.info(request, "Boshqa vazifa ishlayapti.")
    else:
        music_tasks.enqueue("generate_takes", mv, count)
        messages.success(request, f"{count} ta musiqa varianti yaratilmoqda (har biri 1–3 daqiqa). Sahifa o'zi yangilanadi.")
    return redirect("videos:music_detail", pk=pk)


@require_POST
def music_upload_audio(request: HttpRequest, pk: int) -> HttpResponse:
    mv = get_object_or_404(MusicVideo, pk=pk)
    f = request.FILES.get("audio")
    if not f or Path(f.name).suffix.lower() not in AUDIO_EXT:
        messages.error(request, "Musiqa faylini tanlang (mp3, wav, m4a ...).")
    else:
        take = mvs.add_take(mv, f.read(), source="upload", name=f.name)
        messages.success(request, f"Musiqa yuklandi: {take.duration / 60:.1f} daqiqa, sifat bahosi {take.score}/100.")
    return redirect("videos:music_detail", pk=pk)


@require_POST
def music_take_select(request: HttpRequest, pk: int) -> HttpResponse:
    take = get_object_or_404(MusicTake, pk=pk)
    mvs.select_take(take.video, take)
    messages.success(request, "Shu variant video uchun tanlandi.")
    return redirect("videos:music_detail", pk=take.video_id)


@require_POST
def music_combine(request: HttpRequest, pk: int) -> HttpResponse:
    """Play all takes one after another (oldest first) as one track."""
    mv = get_object_or_404(MusicVideo, pk=pk)
    try:
        take = mvs.combine_takes(mv, list(mv.takes.order_by("created_at")))
        messages.success(request, f"Variantlar birlashtirildi: {take.duration / 60:.1f} daqiqalik trek tanlandi.")
    except mvs.MusicError as exc:
        messages.error(request, str(exc))
    return redirect("videos:music_detail", pk=pk)


@require_POST
def music_take_delete(request: HttpRequest, pk: int) -> HttpResponse:
    take = get_object_or_404(MusicTake, pk=pk)
    mv = take.video
    was = take.is_selected
    take.file.delete(save=False)
    take.delete()
    if was:
        nxt = mv.takes.order_by("-score", "-created_at").first()
        if nxt:
            mvs.select_take(mv, nxt)
        else:
            mv.music_file.delete(save=False)
            mv.music_duration = 0
            mv.status = MusicVideo.Status.DRAFT
            mv.save(update_fields=["music_file", "music_duration", "status", "updated_at"])
    return redirect("videos:music_detail", pk=mv.pk)


@require_POST
def music_loop_preview(request: HttpRequest, pk: int) -> HttpResponse:
    """A 20-second clip of the repeat point so the owner can hear whether the join is smooth."""
    import subprocess

    from .services import render

    mv = get_object_or_404(MusicVideo, pk=pk)
    if not mv.music_file:
        messages.error(request, "Avval musiqa yarating yoki yuklang.")
        return redirect("videos:music_detail", pk=pk)
    out = Path(settings.MEDIA_ROOT) / "music" / f"m{mv.pk}" / "loop_preview.mp3"
    out.parent.mkdir(parents=True, exist_ok=True)
    music_sec = mv.music_duration or media_library.audio_duration(Path(mv.music_file.path))
    proc = subprocess.run(music_qc.loop_preview_cmd(render.ffmpeg_exe(), Path(mv.music_file.path), music_sec, out), capture_output=True, text=True)
    if proc.returncode != 0:
        messages.error(request, "Ulanish namunasini yaratib bo'lmadi.")
    else:
        messages.success(request, "Ulanish namunasi tayyor: pastda tinglang.")
    return redirect("videos:music_detail", pk=pk)


@require_POST
def music_upload_clips(request: HttpRequest, pk: int) -> HttpResponse:
    mv = get_object_or_404(MusicVideo, pk=pk)
    files = [f for f in request.FILES.getlist("clips") if Path(f.name).suffix.lower() in VIDEO_EXT]
    room = MAX_CLIPS - mv.clips.count()
    if not files:
        messages.error(request, "Video fayl tanlang (mp4, mov, webm).")
    elif room <= 0:
        messages.error(request, f"Eng ko'pi bilan {MAX_CLIPS} ta klip. Avval bittasini o'chiring.")
    else:
        used = set(mv.clips.values_list("order", flat=True))
        for f in files[:room]:
            order = next(i for i in range(1, MAX_CLIPS + 1) if i not in used)
            used.add(order)
            clip = MusicClip(video=mv, order=order)
            clip.file.save(f.name, f, save=False)
            clip.duration = media_library.audio_duration(clip.file.path)
            clip.save()
        messages.success(request, f"{min(len(files), room)} ta klip yuklandi.")
        if len(files) > room:
            messages.warning(request, f"Faqat {room} tasi olindi (limit {MAX_CLIPS}).")
    return redirect("videos:music_detail", pk=pk)


@require_POST
def music_clip_delete(request: HttpRequest, pk: int) -> HttpResponse:
    clip = get_object_or_404(MusicClip, pk=pk)
    mv_pk = clip.video_id
    clip.file.delete(save=False)
    clip.delete()
    return redirect("videos:music_detail", pk=mv_pk)


@require_POST
def music_render(request: HttpRequest, pk: int) -> HttpResponse:
    mv = get_object_or_404(MusicVideo, pk=pk)
    if mv.is_working:
        messages.info(request, "Boshqa vazifa ishlayapti.")
    elif not mv.music_file:
        messages.error(request, "Avval musiqa yarating yoki yuklang.")
    elif not mv.clips.exists():
        messages.error(request, "Kamida bitta video klip yuklang.")
    else:
        music_tasks.enqueue("render_video", mv)
        messages.success(request, "Montaj boshlandi. Uzun video uchun bir necha o'n daqiqa ketishi mumkin.")
    return redirect("videos:music_detail", pk=pk)


@require_POST
def music_delete(request: HttpRequest, pk: int) -> HttpResponse:
    mv = get_object_or_404(MusicVideo, pk=pk)
    niche = mv.niche
    for f in (mv.music_file, mv.final_video, *[c.file for c in mv.clips.all()], *[t.file for t in mv.takes.all()]):
        if f:
            f.delete(save=False)
    mv.delete()
    return redirect("videos:niche", slug=(niche.slug or f"nisha-{niche.pk}")) if niche else redirect("videos:home")
