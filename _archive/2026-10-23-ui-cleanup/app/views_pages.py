"""Niche, Watch (Tomosha), Channels, Library and Policy pages."""
from __future__ import annotations

from django.conf import settings
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from . import tasks
from .forms import AudioUploadForm, ChannelAddForm, ComplianceRuleForm, NicheForm, PolicyDocumentForm
from .models import (
    ChannelSource, ChannelVideo, ComplianceRule, MusicTrack, Niche, PolicyChangeNote, PolicyDocument, Project,
    SoundEffect, SuggestedTopic,
)
from .services import gemini_client
from .services import media_library as lib
from .services.media_library import parse_tags


def _async(func: str, *args) -> None:
    from django_q.tasks import async_task

    async_task(f"apps.videos.tasks.{func}", *args, task_name=f"{func}-{'-'.join(map(str, args))}"[:100])


# ------------------------------------------------------------------ niche
def niche(request: HttpRequest) -> HttpResponse:
    obj = Niche.active()
    if obj is None:
        obj = Niche.objects.create(name="Mening nisham")
    form = NicheForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Nisha saqlandi. Keyingi ssenariy, rasm va takliflar shu sozlamalar bilan yaratiladi.")
        return redirect("videos:niche")
    stats = {
        "projects": obj.projects.count(),
        "done": obj.projects.filter(status=Project.Status.DONE).count(),
        "channels": obj.channels.count(),
        "suggestions": SuggestedTopic.objects.filter(channel__niche=obj, status=SuggestedTopic.Status.SUGGESTED).count(),
    }
    return render(request, "videos/niche.html", {"niche": obj, "form": form, "stats": stats,
                                                   "channels": obj.channels.all()})


REFERENCE_SCENE = ("character reference sheet: the main character standing alone, full body from head to feet, "
                   "front view, arms relaxed, friendly neutral expression, plain light background, nothing else in the image")


@require_POST
def niche_reference_generate(request: HttpRequest) -> HttpResponse:
    """Draw one clean 'model sheet' of the main character; every scene is compared against it."""
    from django.core.files.base import ContentFile

    from .services.image_providers import ImageProviderError, get_provider
    from .services.images import build_prompt, normalize_to_1080p

    obj = Niche.active()
    if obj is None or not obj.character_description.strip():
        messages.error(request, "Avval 'Asosiy personaj tavsifi' ni yozing va saqlang.")
        return redirect("videos:niche")
    prompt = build_prompt(obj.style_guide or settings.DEFAULT_STYLE_GUIDE,
                          f"the main character {REFERENCE_SCENE}", obj.character_description)
    try:
        png = normalize_to_1080p(get_provider().generate(prompt, seed=4242), mode="letterbox")
    except ImageProviderError as exc:
        messages.error(request, f"Personaj rasmi chizilmadi: {exc}")
        return redirect("videos:niche")
    if obj.character_reference:
        obj.character_reference.delete(save=False)
    obj.character_reference.save("character.png", ContentFile(png), save=True)
    messages.success(request, "Personaj namunasi chizildi. Yoqmasa — yana bir marta bosing yoki o'zingiz rasm yuklang.")
    return redirect("videos:niche")


@require_POST
def niche_reference_delete(request: HttpRequest) -> HttpResponse:
    obj = Niche.active()
    if obj and obj.character_reference:
        obj.character_reference.delete(save=True)
        messages.success(request, "Personaj namunasi o'chirildi.")
    return redirect("videos:niche")


# ------------------------------------------------------------------ watch
def watch(request: HttpRequest) -> HttpResponse:
    mine = Project.objects.exclude(final_video="").exclude(final_video__isnull=True).prefetch_related("thumbnails")
    previews = Project.objects.filter(final_video="").exclude(preview_video="").exclude(preview_video__isnull=True)
    refs = ChannelVideo.objects.select_related("channel").order_by("-view_count")[:24]
    return render(request, "videos/watch.html", {"mine": mine, "previews": previews, "refs": refs})


def watch_project(request: HttpRequest, pk: int) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    others = Project.objects.exclude(pk=pk).exclude(final_video="").exclude(final_video__isnull=True)[:8]
    return render(request, "videos/watch_project.html", {"project": project, "others": others})


def watch_reference(request: HttpRequest, pk: int) -> HttpResponse:
    video = get_object_or_404(ChannelVideo.objects.select_related("channel"), pk=pk)
    more = video.channel.videos.exclude(pk=pk).order_by("-view_count")[:8]
    return render(request, "videos/watch_reference.html", {"video": video, "more": more})


# ------------------------------------------------------------------ channels
def channels(request: HttpRequest) -> HttpResponse:
    form = ChannelAddForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if not settings.YOUTUBE_API_KEY.strip():
            messages.error(request, ".env faylida YOUTUBE_API_KEY yo'q — kanalni o'qib bo'lmaydi.")
        else:
            ch = ChannelSource.objects.create(
                name=form.cleaned_data["url"], handle_or_url=form.cleaned_data["url"], niche=Niche.active(),
                state=ChannelSource.State.WORKING, progress_message="Navbatda...")
            _async("channel_research", ch.pk)
            messages.success(request, "Kanal qo'shildi. Tahlil fonda boshlandi — 1-2 daqiqa kuting.")
            return redirect("videos:channel_detail", pk=ch.pk)
    items = ChannelSource.objects.annotate(
        n_videos=Count("videos", distinct=True),
        n_sugg=Count("suggestions", filter=Q(suggestions__status=SuggestedTopic.Status.SUGGESTED), distinct=True),
    )
    return render(request, "videos/channels.html", {
        "form": form, "channels": items, "gemini_ok": gemini_client.is_configured(),
        "youtube_ok": bool(settings.YOUTUBE_API_KEY.strip()),
    })


def channel_detail(request: HttpRequest, pk: int) -> HttpResponse:
    ch = get_object_or_404(ChannelSource, pk=pk)
    videos = list(ch.videos.all())
    top = sorted(videos, key=lambda v: v.view_count, reverse=True)[:6]
    avg_len = round(sum(v.duration_sec for v in videos) / len(videos) / 60, 1) if videos else None
    ctx = {
        "ch": ch, "videos": videos, "top": top, "avg_len": avg_len,
        "total_views": sum(v.view_count for v in videos),
        "suggestions": ch.suggestions.filter(status=SuggestedTopic.Status.SUGGESTED),
        "used": ch.suggestions.filter(status=SuggestedTopic.Status.USED),
        "gemini_ok": gemini_client.is_configured(),
        "notes": [ln.split(":", 1) for ln in ch.style_notes.split("\n\n") if ":" in ln],
    }
    return render(request, "videos/channel_detail.html", ctx)


def channel_status(request: HttpRequest, pk: int) -> HttpResponse:
    ch = get_object_or_404(ChannelSource, pk=pk)
    return render(request, "videos/partials/channel_status.html", {"ch": ch, "was_busy": request.GET.get("poll") == "1"})


@require_POST
def channel_refresh(request: HttpRequest, pk: int) -> HttpResponse:
    ch = get_object_or_404(ChannelSource, pk=pk)
    if ch.state != ChannelSource.State.WORKING:
        ChannelSource.objects.filter(pk=pk).update(state=ChannelSource.State.WORKING, progress_message="Navbatda...")
        _async("channel_research", ch.pk, request.POST.get("suggest") == "1")
    return redirect("videos:channel_detail", pk=pk)


@require_POST
def channel_suggest(request: HttpRequest, pk: int) -> HttpResponse:
    ch = get_object_or_404(ChannelSource, pk=pk)
    if not gemini_client.is_configured():
        messages.error(request, "Takliflar uchun .env da GEMINI_API_KEY va GEMINI_TEXT_MODEL kerak.")
    elif ch.state != ChannelSource.State.WORKING:
        ChannelSource.objects.filter(pk=pk).update(state=ChannelSource.State.WORKING, progress_message="Yangi mavzular o'ylanmoqda...")
        _async("channel_suggest_more", ch.pk)
    return redirect("videos:channel_detail", pk=pk)


@require_POST
def channel_delete(request: HttpRequest, pk: int) -> HttpResponse:
    get_object_or_404(ChannelSource, pk=pk).delete()
    messages.success(request, "Kanal o'chirildi.")
    return redirect("videos:channels")


@require_POST
def suggestion_add(request: HttpRequest) -> HttpResponse:
    """Add a topic idea by hand (from the "Yangi video" page)."""
    from .forms import ManualSuggestionForm
    from .services.topics import find_similar, find_similar_projects

    form = ManualSuggestionForm(request.POST)
    if not form.is_valid():
        for errors in form.errors.values():
            messages.error(request, " ".join(errors))
        return redirect("videos:home")
    text = form.cleaned_data["topic_text"]
    waiting = SuggestedTopic.objects.filter(status=SuggestedTopic.Status.SUGGESTED).values_list("pk", "topic_text")
    if find_similar(text, waiting, threshold=0.85):
        messages.warning(request, "Bu mavzu takliflar ro'yxatida allaqachon bor.")
        return redirect("videos:home")
    SuggestedTopic.objects.create(topic_text=text, rationale=form.cleaned_data["rationale"].strip())
    made = find_similar_projects(text)
    if made:
        messages.warning(request, f"Mavzu qo'shildi, lekin unga o'xshash video bor: «{made[0].topic}».")
    else:
        messages.success(request, "Mavzu takliflarga qo'shildi.")
    return redirect("videos:home")


@require_POST
def suggestion_dismiss(request: HttpRequest, pk: int) -> HttpResponse:
    s = get_object_or_404(SuggestedTopic, pk=pk)
    s.status = SuggestedTopic.Status.DISMISSED
    s.save(update_fields=["status"])
    if request.headers.get("HX-Request") == "true":
        return HttpResponse("")
    if s.channel_id is None:
        return redirect(request.POST.get("next") or "videos:home")
    return redirect(request.POST.get("next") or "videos:channel_detail", pk=s.channel_id)


# ------------------------------------------------------------------ library
def library(request: HttpRequest) -> HttpResponse:
    tab = request.GET.get("tab", "music")
    tag = request.GET.get("tag", "").strip().lower()
    form = AudioUploadForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        tab = request.POST.get("tab", tab)
        if form.is_valid():
            d = form.cleaned_data
            tags = parse_tags(d["tags"]) or None
            files = d["files"]
            title = d["title"] if len(files) == 1 else ""
            for f in files:
                if tab == "sfx":
                    lib.add_sfx(f, name=title, tags=tags)
                else:
                    lib.add_track(f, title=title, tags=tags, license_note=d["license_note"])
            messages.success(request, f"{len(files)} ta fayl yuklandi. Teglarni tekshirib, kerak bo'lsa o'zgartiring.")
            return redirect(f"{request.path}?tab={tab}")
    music = list(MusicTrack.objects.all())
    sfx = list(SoundEffect.objects.all())
    if tag:
        music = [m for m in music if tag in [t.lower() for t in m.mood_tags or []]]
        sfx = [s for s in sfx if tag in [t.lower() for t in s.tags or []]]
    return render(request, "videos/library.html", {
        "tab": tab, "tag": tag, "form": form, "music": music, "sfx": sfx,
        "moods": settings.MUSIC_MOODS, "sfx_tags": settings.SFX_TAGS,
        "missing": lib.missing_sfx_tags(), "starter": lib.starter_pack_available(),
        "counts": {"music": MusicTrack.objects.count(), "sfx": SoundEffect.objects.count()},
        "total_minutes": round((MusicTrack.objects.aggregate(s=Sum("duration"))["s"] or 0) / 60),
    })


@require_POST
def library_starter(request: HttpRequest) -> HttpResponse:
    m, s = lib.import_starter_pack()
    messages.success(request, f"Boshlang'ich to'plam: {m} ta musiqa va {s} ta ovoz effekti qo'shildi."
                     if (m or s) else "Boshlang'ich to'plam allaqachon yuklangan.")
    return redirect("videos:library")


@require_POST
def library_tags(request: HttpRequest, kind: str, pk: int) -> HttpResponse:
    obj = get_object_or_404(MusicTrack if kind == "music" else SoundEffect, pk=pk)
    tags = parse_tags(request.POST.get("tags", ""))
    if kind == "music":
        obj.mood_tags = tags
        obj.title = request.POST.get("title", obj.title).strip() or obj.title
        obj.license_note = request.POST.get("license_note", obj.license_note)
    else:
        obj.tags = tags
        obj.name = request.POST.get("title", obj.name).strip() or obj.name
    obj.save()
    return render(request, "videos/partials/library_row.html", {"item": obj, "kind": kind, "saved": True})


@require_POST
def library_delete(request: HttpRequest, kind: str, pk: int) -> HttpResponse:
    obj = get_object_or_404(MusicTrack if kind == "music" else SoundEffect, pk=pk)
    lib.delete_media_file(obj)
    obj.delete()
    return HttpResponse("")


# ------------------------------------------------------------------ policy
def policy(request: HttpRequest) -> HttpResponse:
    from django_q.models import Schedule

    doc_form = PolicyDocumentForm(prefix="doc")
    rule_form = ComplianceRuleForm(prefix="rule")
    sched = Schedule.objects.filter(name="policy-watch").first()
    return render(request, "videos/policy.html", {
        "docs": PolicyDocument.objects.all(),
        "notes": PolicyChangeNote.objects.select_related("policy_document")[:50],
        "rules": ComplianceRule.objects.all(),
        "doc_form": doc_form, "rule_form": rule_form,
        "interval": settings.POLICY_CHECK_INTERVAL_DAYS, "next_run": sched.next_run if sched else None,
        "gemini_ok": gemini_client.is_configured(),
    })


@require_POST
def policy_check(request: HttpRequest) -> HttpResponse:
    doc_id = request.POST.get("doc")
    if doc_id:
        _async("policy_check_one", int(doc_id))
    else:
        _async("policy_check_all")
    messages.success(request, "Tekshiruv fonda boshlandi. 10-30 soniyadan keyin sahifani yangilang.")
    return redirect("videos:policy")


@require_POST
def policy_doc_save(request: HttpRequest) -> HttpResponse:
    pk = request.POST.get("pk")
    if request.POST.get("delete") and pk:
        PolicyDocument.objects.filter(pk=pk).delete()
        messages.success(request, "Sahifa ro'yxatdan olib tashlandi.")
        return redirect("videos:policy")
    inst = PolicyDocument.objects.filter(pk=pk).first() if pk else None
    form = PolicyDocumentForm(request.POST, instance=inst, prefix="doc")
    if form.is_valid():
        doc = form.save()
        if inst is None:
            _async("policy_check_one", doc.pk)
        messages.success(request, "Saqlandi.")
    else:
        messages.error(request, "Nomi va to'g'ri URL kiriting.")
    return redirect("videos:policy")


@require_POST
def policy_doc_toggle(request: HttpRequest, pk: int) -> HttpResponse:
    doc = get_object_or_404(PolicyDocument, pk=pk)
    doc.enabled = not doc.enabled
    doc.save(update_fields=["enabled"])
    return redirect("videos:policy")


@require_POST
def policy_note_review(request: HttpRequest, pk: int) -> HttpResponse:
    note = get_object_or_404(PolicyChangeNote, pk=pk)
    note.reviewed = not note.reviewed
    note.save(update_fields=["reviewed"])
    return redirect("videos:policy")


@require_POST
def policy_notes_review_all(request: HttpRequest) -> HttpResponse:
    PolicyChangeNote.objects.filter(reviewed=False).update(reviewed=True)
    return redirect("videos:policy")


@require_POST
def policy_rule_save(request: HttpRequest) -> HttpResponse:
    pk = request.POST.get("pk")
    if request.POST.get("delete") and pk:
        ComplianceRule.objects.filter(pk=pk).delete()
        return redirect("videos:policy")
    inst = ComplianceRule.objects.filter(pk=pk).first() if pk else None
    form = ComplianceRuleForm(request.POST, instance=inst, prefix="rule")
    if form.is_valid():
        rule = form.save(commit=False)
        if inst is None:
            rule.order = (ComplianceRule.objects.order_by("-order").values_list("order", flat=True).first() or 0) + 1
        rule.save()
        messages.success(request, "Tekshiruv bandi saqlandi.")
    else:
        messages.error(request, "Band saqlanmadi: nomi va ko'rsatmani to'ldiring.")
    return redirect("videos:policy")
