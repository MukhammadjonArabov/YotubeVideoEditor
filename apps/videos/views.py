"""Slim site: a dashboard (statistics, videos in progress, finished videos) and one page per video
(player, downloads and the publish kit: 3 titles, 1 description, tags, 3 thumbnails).

Everything else (script import, approval, images, voice, render) is run through Claude with the management
commands, so the site only shows results. UI text is Uzbek.
"""
from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.db.models import Count, Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import MusicVideo, Niche, Project, Scene
from .services import kit as kitsvc
from .services import dub as dubsvc


def _mmss(seconds: float | None) -> str:
    s = int(seconds or 0)
    return f"{s // 60}:{s % 60:02d}"


def _cover_url(project: Project, kit: dict) -> str:
    if kit["previews"]:
        return kit["previews"][0]["url"]
    scene = project.scenes.exclude(image="").order_by("order").first()
    return scene.image.url if scene else ""


def _niche_numbers(projects_qs) -> dict:
    """Counts used on the niche card and the niche page."""
    done = list(projects_qs.filter(status=Project.Status.DONE).order_by("-finished_at", "-pk"))
    total_sec = sum(p.actual_duration_sec or 0 for p in done)
    working = [p for p in projects_qs.exclude(status=Project.Status.DONE).exclude(status=Project.Status.DRAFT) if p.status != Project.Status.FAILED]
    return {"done": done, "working": working, "total_sec": total_sec}


def _music_card(niche: Niche) -> dict:
    items = list(MusicVideo.objects.filter(niche=niche))
    done = [m for m in items if m.status == MusicVideo.Status.DONE]
    return {"niche": niche, "name": niche.name, "emoji": niche.emoji, "slug": niche.slug or f"nisha-{niche.pk}",
            "description": niche.description, "done": len(done), "working": len(items) - len(done), "cover": "",
            "length": _mmss(sum(m.actual_duration_sec or 0 for m in done)), "language": niche.language.upper()}


def _card(niche: Niche | None, projects_qs) -> dict:
    if niche is not None and niche.kind == "music":
        return _music_card(niche)
    n = _niche_numbers(projects_qs)
    cover = ""
    for p in n["done"][:6]:
        cover = _cover_url(p, kitsvc.load_kit(p))
        if cover:
            break
    return {"niche": niche, "name": niche.name if niche else "Boshqa videolar", "emoji": niche.emoji if niche else "🎬",
            "slug": (niche.slug or f"nisha-{niche.pk}") if niche else "boshqa", "description": (niche.description if niche else ""),
            "done": len(n["done"]), "working": len(n["working"]), "length": _mmss(n["total_sec"]), "cover": cover,
            "language": (niche.language if niche else "en").upper()}


def home(request: HttpRequest) -> HttpResponse:
    """The front page: one card per niche (yo'nalish), with its video count and a cover."""
    cards = [_card(n, Project.objects.filter(niche=n)) for n in Niche.objects.order_by("id")]
    loose = Project.objects.filter(niche__isnull=True)
    if loose.exists():
        cards.append(_card(None, loose))
    done_qs = Project.objects.filter(status=Project.Status.DONE)
    total_sec = sum(p.actual_duration_sec or 0 for p in done_qs)
    totals = [("Yo'nalishlar", len(cards), "ta"), ("Tayyor videolar", done_qs.count(), "ta"),
              ("Jami davomiylik", _mmss(total_sec), "daqiqa")]
    return render(request, "videos/home.html", {"cards": cards, "totals": totals,
                                                "refresh": Project.objects.filter(is_working=True).exists()})


def niche_detail(request: HttpRequest, slug: str) -> HttpResponse:
    """One niche: its statistics, videos being made and the finished videos."""
    if slug == "boshqa":
        niche, projects = None, Project.objects.filter(niche__isnull=True)
    else:
        niche = (get_object_or_404(Niche, pk=int(slug[6:])) if slug.startswith("nisha-") and slug[6:].isdigit()
                 else get_object_or_404(Niche, slug=slug))
        if niche.kind == "music":
            from . import views_music

            return views_music.niche_page(request, niche)
        projects = Project.objects.filter(niche=niche)
    numbers = _niche_numbers(projects)
    done_qs = projects.filter(status=Project.Status.DONE)
    now = timezone.now()
    done = []
    for p in numbers["done"]:
        kit = kitsvc.load_kit(p)
        done.append({"p": p, "cover": _cover_url(p, kit), "length": _mmss(p.actual_duration_sec),
                     "title": p.title or p.topic, "has_kit": bool(kit["titles"])})
    working = numbers["working"]
    scene_stats = Scene.objects.filter(project__in=done_qs).aggregate(n=Count("id"))
    spent = projects.aggregate(s=Sum("image_cost"))["s"] or Decimal("0")
    total_sec = numbers["total_sec"]
    stats = [
        ("Tayyor videolar", len(done), "ta"),
        ("Jami davomiylik", _mmss(total_sec), "daqiqa"),
        ("O'rtacha video", _mmss(total_sec / len(done)) if done else "0:00", "daqiqa"),
        ("So'nggi 7 kunda", done_qs.filter(finished_at__gte=now - timedelta(days=7)).count(), "ta video"),
        ("So'nggi 30 kunda", done_qs.filter(finished_at__gte=now - timedelta(days=30)).count(), "ta video"),
        ("Jarayonda", len(working), "ta"),
        ("Chizilgan sahnalar", scene_stats["n"], "ta rasm"),
        ("Rasmlarga sarf", f"${Decimal(spent):.2f}", "jami"),
    ]
    return render(request, "videos/niche_detail.html", {
        "niche": niche, "title": niche.name if niche else "Boshqa videolar", "emoji": niche.emoji if niche else "🎬",
        "stats": stats, "done": done, "working": working, "refresh": any(p.is_working for p in working)})


def video_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """One video: player, downloads and the publish kit."""
    p = get_object_or_404(Project, pk=pk)
    kit = kitsvc.load_kit(p)
    srt = Path(settings.MEDIA_ROOT) / "projects" / f"p{p.pk}" / "render" / "final.srt"
    srt_url = f"{settings.MEDIA_URL}projects/p{p.pk}/render/final.srt" if srt.exists() else ""
    titles = [{"text": t, "chars": len(t)} for t in kit["titles"]]
    return render(request, "videos/video_detail.html", {
        "p": p, "niche": p.niche, "kit": kit, "titles": titles, "srt_url": srt_url, "length": _mmss(p.actual_duration_sec),
        "video_url": p.final_video.url if p.final_video else "", "tags_text": ", ".join(kit["tags"]),
        "tags_len": len(", ".join(kit["tags"])), "dubs": dubsvc.tracks(p),
    })
