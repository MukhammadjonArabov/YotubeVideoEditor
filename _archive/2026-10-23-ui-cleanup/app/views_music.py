"""Music-video section: relaxing long videos (one looped track + looped clips + Subscribe / Like)."""
from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from . import music_tasks
from .models import MusicClip, MusicVideo
from .services import media_library
from .services import music_video as mvs

VIDEO_EXT = {".mp4", ".mov", ".webm", ".m4v"}
AUDIO_EXT = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"}
MAX_CLIPS = 4


def _int(value, default: int, lo: int, hi: int) -> int:
    try:
        return max(lo, min(hi, int(value)))
    except (TypeError, ValueError):
        return default


def music_list(request: HttpRequest) -> HttpResponse:
    return render(request, "videos/music_list.html", {"items": MusicVideo.objects.all()})


@require_POST
def music_create(request: HttpRequest) -> HttpResponse:
    title = (request.POST.get("title") or "").strip() or "Tinchlantiruvchi tabiat musiqasi"
    mv = MusicVideo.objects.create(title=title[:200], music_prompt=mvs.DEFAULT_MUSIC_PROMPT)
    return redirect("videos:music_detail", pk=mv.pk)


def music_detail(request: HttpRequest, pk: int) -> HttpResponse:
    mv = get_object_or_404(MusicVideo, pk=pk)
    return render(request, "videos/music_detail.html", {
        "mv": mv, "clips": list(mv.clips.all()), "flow_prompts": mvs.FLOW_CLIP_PROMPTS, "max_clips": MAX_CLIPS,
        "ctas": len(mvs.plan_ctas(mv.target_minutes * 60, mv.cta_every_min, mv.add_subscribe, mv.add_like)) // (
            (1 if mv.add_subscribe else 0) + (1 if mv.add_like else 0) or 1),
        "can_render": bool(mv.music_file) and mv.clips.exists() and not mv.is_working,
    })


@require_POST
def music_save(request: HttpRequest, pk: int) -> HttpResponse:
    mv = get_object_or_404(MusicVideo, pk=pk)
    p = request.POST
    mv.title = (p.get("title") or mv.title).strip()[:200]
    mv.music_prompt = (p.get("music_prompt") or "").strip()
    mv.music_minutes = _int(p.get("music_minutes"), mv.music_minutes, 3, 10)
    mv.target_minutes = _int(p.get("target_minutes"), mv.target_minutes, 5, 180)
    mv.cta_every_min = _int(p.get("cta_every_min"), mv.cta_every_min, 1, 60)
    mv.add_subscribe = p.get("add_subscribe") == "on"
    mv.add_like = p.get("add_like") == "on"
    mv.save()
    messages.success(request, "Saqlandi.")
    return redirect("videos:music_detail", pk=pk)


@require_POST
def music_generate(request: HttpRequest, pk: int) -> HttpResponse:
    mv = get_object_or_404(MusicVideo, pk=pk)
    if mv.is_working:
        messages.info(request, "Boshqa vazifa ishlayapti.")
    else:
        music_tasks.enqueue("generate_music", mv)
        messages.success(request, "Musiqa yaratilmoqda (1–3 daqiqa). Sahifa o'zi yangilanadi.")
    return redirect("videos:music_detail", pk=pk)


@require_POST
def music_upload_audio(request: HttpRequest, pk: int) -> HttpResponse:
    mv = get_object_or_404(MusicVideo, pk=pk)
    f = request.FILES.get("audio")
    if not f or not any(f.name.lower().endswith(e) for e in AUDIO_EXT):
        messages.error(request, "Musiqa faylini tanlang (mp3, wav, m4a ...).")
    else:
        mvs.save_music(mv, f.read(), f.name)
        messages.success(request, f"Musiqa yuklandi: {mv.music_duration / 60:.1f} daqiqa.")
    return redirect("videos:music_detail", pk=pk)


@require_POST
def music_upload_clips(request: HttpRequest, pk: int) -> HttpResponse:
    mv = get_object_or_404(MusicVideo, pk=pk)
    files = [f for f in request.FILES.getlist("clips") if any(f.name.lower().endswith(e) for e in VIDEO_EXT)]
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
    for f in (mv.music_file, mv.final_video, *[c.file for c in mv.clips.all()]):
        if f:
            f.delete(save=False)
    mv.delete()
    return redirect("videos:music_list")
