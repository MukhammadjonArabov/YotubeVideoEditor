"""JSON API used by the Chrome extension (flow_extension/) + the buttons on the Flow page.

The API is for the extension only: every call needs the shared token (X-Flow-Token). It is csrf-exempt on
purpose (the extension is not a browser form), the token is what keeps other web pages out.
"""
from __future__ import annotations

import json
import secrets

from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import FlowJob, Project
from .services import flow_queue

MAX_UPLOAD = 200 * 1024 * 1024


def _authorized(request: HttpRequest) -> bool:
    given = request.headers.get("X-Flow-Token", "")
    return bool(given) and secrets.compare_digest(given, settings.FLOW_API_TOKEN)


def _guard(view):
    def wrapper(request, *args, **kwargs):
        if not _authorized(request):
            return JsonResponse({"error": "token noto'g'ri"}, status=401)
        return view(request, *args, **kwargs)

    wrapper.__name__ = view.__name__
    return csrf_exempt(wrapper)


def _job_json(job: FlowJob) -> dict:
    return {"id": job.pk, "kind": job.kind, "prompt": job.prompt, "scene": job.scene.order, "project": job.project_id,
            "attempt": job.attempts, "frame": flow_queue.start_frame(job) is not None,
            "character": job.project.flow_character}


@_guard
@require_GET
def api_next(request: HttpRequest) -> JsonResponse:
    job = flow_queue.claim_next(request.GET.get("kind"))
    return JsonResponse({"job": _job_json(job) if job else None, "counts": flow_queue.counts()})


@_guard
@require_GET
def api_frame(request: HttpRequest, pk: int) -> HttpResponse:
    job = get_object_or_404(FlowJob.objects.select_related("scene"), pk=pk)
    data = flow_queue.start_frame(job)
    if data is None:
        return JsonResponse({"error": "boshlang'ich kadr yo'q"}, status=404)
    return HttpResponse(data, content_type="image/png")


@_guard
@require_POST
def api_result(request: HttpRequest, pk: int) -> JsonResponse:
    job = get_object_or_404(FlowJob.objects.select_related("scene", "scene__project", "project"), pk=pk)
    upload = request.FILES.get("file")
    if not upload or upload.size > MAX_UPLOAD:
        return JsonResponse({"error": "fayl yo'q yoki juda katta"}, status=400)
    job = flow_queue.complete(job, upload.read(), upload.name)
    return JsonResponse({"status": job.status, "note": job.note})


@_guard
@require_POST
def api_fail(request: HttpRequest, pk: int) -> JsonResponse:
    job = get_object_or_404(FlowJob, pk=pk)
    try:
        body = json.loads(request.body or b"{}")
    except ValueError:
        body = {}
    error = body.get("error", "")
    job = flow_queue.requeue(job, error) if body.get("requeue") else flow_queue.fail(job, error)
    return JsonResponse({"status": job.status, "note": job.note})


@_guard
@require_POST
def api_diagnose(request: HttpRequest) -> JsonResponse:
    """The extension's "Diagnoz": what the Flow page looks like (buttons, inputs...), saved for fixing selectors."""
    out = settings.TEMP_DIR / "flow_diagnose.json"
    out.write_bytes(request.body[:2_000_000])
    return JsonResponse({"saved": str(out)})


@_guard
@require_GET
def api_status(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"counts": flow_queue.counts()})


# ------------------------------------------------------------------ buttons on the Flow page
@require_POST
def flow_enqueue(request: HttpRequest, pk: int) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    kind = FlowJob.Kind.VIDEO if request.POST.get("kind") == "video" else FlowJob.Kind.IMAGE
    n = flow_queue.enqueue(project, kind, only_missing=request.POST.get("all") != "1",
                           hook_only=request.POST.get("scope") != "all")
    if n:
        messages.success(request, f"{n} ta {FlowJob.Kind(kind).label.lower()} navbatga qo'yildi. "
                                  "Flow ochiq Chrome'da kengaytmani yoqing.")
    elif kind == FlowJob.Kind.VIDEO:
        messages.info(request, "Navbatga qo'yadigan hook sahnasi yo'q: avval hook rasmlari kerak (yoki hammasi tayyor).")
    else:
        messages.info(request, "Rasmsiz sahna qolmagan yoki hammasi navbatda.")
    return redirect("videos:project_flow_prompts", pk=pk)


@require_POST
def flow_job_action(request: HttpRequest, pk: int, action: str) -> HttpResponse:
    job = get_object_or_404(FlowJob, pk=pk)
    if action == "approve":
        flow_queue.approve(job)
        messages.success(request, f"{job.scene.order}-sahna natijasi qabul qilindi.")
    elif action == "retry":
        flow_queue.retry(job)
        messages.info(request, f"{job.scene.order}-sahna qayta navbatga qo'yildi.")
    elif action == "cancel":
        job.delete()
    return redirect("videos:project_flow_prompts", pk=job.project_id)


@require_POST
def flow_auto_render_toggle(request: HttpRequest, pk: int) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    project.flow_auto_render = request.POST.get("on") == "1"
    project.save(update_fields=["flow_auto_render", "updated_at"])
    messages.success(request, "Flow tugagach video avtomatik yaratiladi." if project.flow_auto_render
                     else "Avtomatik montaj o'chirildi.")
    return redirect("videos:project_flow_prompts", pk=pk)


@require_POST
def flow_character_save(request: HttpRequest, pk: int) -> HttpResponse:
    """The hero's name in Flow's Characters section: put into prompts and attached by the extension."""
    from .services import manual_images

    project = get_object_or_404(Project, pk=pk)
    raw = request.POST.get("name", "").strip()
    name = manual_images.clean_character_name(raw)
    if raw and not name:
        messages.warning(request, "Nom pastki chiziqli bo'lsin, masalan: main_hero")
        return redirect("videos:project_flow_prompts", pk=pk)
    project.flow_character = name
    project.save(update_fields=["flow_character", "updated_at"])
    messages.success(request, f"Qahramon nomi saqlandi: {name}. Promptlar shu nom bilan yangilanadi." if name
                     else "Qahramon nomi o'chirildi.")
    return redirect("videos:project_flow_prompts", pk=pk)
