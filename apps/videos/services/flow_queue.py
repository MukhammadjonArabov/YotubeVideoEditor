"""Queue between the app and the Chrome extension that drives Google Flow (flow_extension/).

The app puts one FlowJob per scene (prompt + kind). The extension takes the next job, types the prompt into
Flow, waits for the result, downloads it and sends the bytes back. Here every result is checked before it
is used: images by the vision check (same hero check as the other image providers), videos by ffmpeg
(long enough, not black / frozen). A bad result sends the job back to the queue (FLOW_MAX_ATTEMPTS tries,
every try spends Flow credits), after that it waits for a human decision (status "review").
"""
from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from ..models import FlowJob, Project, Scene
from . import hook_video, manual_images

logger = logging.getLogger(__name__)

STALE_MINUTES = 20  # a job "in Flow" for longer than this is given back (tab closed, extension stopped)
MIN_VIDEO_SEC = 2.0


# ------------------------------------------------------------------ queue
def export_dir(project: Project) -> Path:
    """Every accepted Flow result is also copied here under a scene-numbered name (on the project drive)."""
    from .files import project_media_dir

    d = project_media_dir(project.pk) / "flow_export"
    d.mkdir(parents=True, exist_ok=True)
    return d


def export_name(job: FlowJob) -> str:
    ext = Path(job.result.name).suffix.lower() or (".mp4" if job.kind == FlowJob.Kind.VIDEO else ".png")
    return f"scene_{job.scene.order:03d}_{job.kind}{ext}"  # scene_001_image.png / scene_001_video.mp4


def export_result(job: FlowJob) -> Path:
    """Copy of the Flow file as scene_<number>_<image|video>.<ext>: easy to tell apart when editing by hand."""
    folder = export_dir(job.project)
    target = folder / export_name(job)
    for old in folder.glob(f"scene_{job.scene.order:03d}_{job.kind}.*"):  # a newer take replaces the older one
        old.unlink(missing_ok=True)
    shutil.copyfile(job.result.path, target)
    return target


def enqueue(project: Project, kind: str, only_missing: bool = True, hook_only: bool = True) -> int:
    """Create jobs for the scenes that still need `kind`. Returns how many were added.
    Videos: hook scenes only by default; hook_only=False asks for a clip for EVERY scene (many Flow credits)."""
    scenes = list(project.scenes.order_by("order"))
    if kind == FlowJob.Kind.VIDEO:
        if hook_only:
            scenes = [s for s in scenes if s.beat_type == "hook"]
        if only_missing:
            scenes = [s for s in scenes if not s.video]
        # a clip starts from the scene's picture: no picture, no clip
        scenes = [s for s in scenes if s.image]
        prompts = {s.pk: hook_video.video_prompt(s) for s in scenes}
    else:
        if only_missing:
            scenes = [s for s in scenes if not s.image]
        prompts = {s.pk: manual_images.flow_prompt(project, s, project.flow_character) for s in scenes}
    busy = set(FlowJob.objects.filter(project=project, kind=kind, status__in=[
        FlowJob.Status.PENDING, FlowJob.Status.RUNNING, FlowJob.Status.REVIEW]).values_list("scene_id", flat=True))
    new = [FlowJob(project=project, scene=s, kind=kind, prompt=prompts[s.pk]) for s in scenes if s.pk not in busy]
    FlowJob.objects.bulk_create(new)
    return len(new)


ACTIVE = (FlowJob.Status.PENDING, FlowJob.Status.RUNNING, FlowJob.Status.REVIEW)
PRODUCE_OK = {Project.Status.APPROVED, Project.Status.DONE, Project.Status.FAILED}


def scenes_waiting_for_flow(project: Project) -> set[int]:
    """Scene ids that still have an open Flow job: the normal image step must not draw them itself."""
    return set(FlowJob.objects.filter(project=project, status__in=ACTIVE).values_list("scene_id", flat=True))


def maybe_auto_render(project_id: int) -> bool:
    """Flow queue finished and the owner asked for it: voice + montage start by themselves (one time only)."""
    from .. import tasks

    project = Project.objects.get(pk=project_id)
    if not project.flow_auto_render or project.is_working or project.status not in PRODUCE_OK:
        return False
    if FlowJob.objects.filter(project=project, status__in=ACTIVE).exists() or not project.scenes.exists():
        return False
    Project.objects.filter(pk=project_id).update(flow_auto_render=False, progress_message="Flow tugadi - montaj navbatda...")
    tasks.enqueue("produce_video", project, "final")
    return True


def release_stale() -> int:
    cutoff = timezone.now() - timedelta(minutes=STALE_MINUTES)
    return FlowJob.objects.filter(status=FlowJob.Status.RUNNING, claimed_at__lt=cutoff).update(
        status=FlowJob.Status.PENDING, note="Flow javob bermadi - qayta navbatga qo'yildi")


@transaction.atomic
def claim_next(kind: str | None = None) -> FlowJob | None:
    """Oldest pending job (images before videos: a clip needs its picture first), marked as running.
    `kind` ("image" | "video") lets the extension work only on what Flow is currently set up for."""
    release_stale()
    qs = FlowJob.objects.select_for_update(skip_locked=True).select_related("scene", "project").filter(
        status=FlowJob.Status.PENDING)
    if kind in (FlowJob.Kind.IMAGE, FlowJob.Kind.VIDEO):
        qs = qs.filter(kind=kind)
    job = qs.order_by("kind", "project_id", "scene__order").first()
    if job is None:
        return None
    job.status = FlowJob.Status.RUNNING
    job.attempts += 1
    job.claimed_at = timezone.now()
    job.save(update_fields=["status", "attempts", "claimed_at", "updated_at"])
    return job


def counts(project: Project | None = None) -> dict[str, int]:
    qs = FlowJob.objects.filter(project=project) if project else FlowJob.objects.all()
    return {s: qs.filter(status=s).count() for s in FlowJob.Status.values}


def start_frame(job: FlowJob) -> bytes | None:
    """The scene's picture, which Flow's "Frames to video" uses as the first frame."""
    if job.kind != FlowJob.Kind.VIDEO or not job.scene.image:
        return None
    return Path(job.scene.image.path).read_bytes()


# ------------------------------------------------------------------ checks
def check_video(path: Path) -> tuple[bool, str]:
    """(ok, reason). Never blocks on its own failure: no ffmpeg / unreadable stats -> accepted."""
    from PIL import Image, ImageChops, ImageStat

    from . import media_library, render

    length = media_library.audio_duration(path)
    if length and length < MIN_VIDEO_SEC:
        return False, f"klip juda qisqa ({length:.1f} s)"
    frames = []
    try:
        exe = render.ffmpeg_exe()
        with tempfile.TemporaryDirectory() as tmp:
            for k, at in enumerate((0.2, max(0.3, (length or 4) / 2), max(0.4, (length or 4) - 0.3))):
                out = Path(tmp) / f"f{k}.png"
                subprocess.run([exe, "-y", "-loglevel", "error", "-ss", f"{at:.2f}", "-i", str(path), "-frames:v", "1",
                                "-vf", "scale=160:-1", str(out)], check=True, timeout=60)
                with Image.open(out) as im:
                    frames.append(im.convert("L").copy())
    except Exception as exc:  # noqa: BLE001
        logger.warning("Video check skipped: %s", str(exc)[:200])
        return True, ""
    means = [ImageStat.Stat(f).mean[0] for f in frames]
    if max(means) < 12:
        return False, "kadrlar qora"
    if min(means) > 250:
        return False, "kadrlar oppoq"
    motion = ImageStat.Stat(ImageChops.difference(frames[0], frames[-1])).mean[0]
    if motion < 1.0:
        return False, "klip qotib qolgan (harakat yo'q)"
    return True, ""


def check_image(job: FlowJob, data: bytes) -> tuple[bool, str]:
    from .image_qa import check_scene_image
    from .images import character_reference_bytes, mentions_main_character

    scene = job.scene
    if not mentions_main_character(scene.image_prompt):
        return True, ""
    res = check_scene_image(data, scene.project.character_description, scene.image_prompt,
                            character_reference_bytes(scene.project))
    return res.ok, res.reason


class _Upload:
    def __init__(self, name: str, data: bytes):
        self.name, self._data = name, data

    def read(self) -> bytes:
        return self._data


# ------------------------------------------------------------------ results
def complete(job: FlowJob, data: bytes, filename: str) -> FlowJob:
    """A downloaded result from the extension: keep it, check it, then use it or send the job back."""
    if job.result:
        job.result.delete(save=False)
    job.result.save(filename or "result.bin", ContentFile(data), save=False)
    job.save(update_fields=["result", "updated_at"])
    if job.kind == FlowJob.Kind.VIDEO:
        ok, reason = check_video(Path(job.result.path))
    else:
        ok, reason = check_image(job, data)
    if ok:
        apply(job)
        job.status, job.note = FlowJob.Status.DONE, ""
    elif job.attempts < settings.FLOW_MAX_ATTEMPTS:
        job.status, job.note = FlowJob.Status.PENDING, f"Qayta urinish: {reason}"
    else:
        job.status, job.note = FlowJob.Status.REVIEW, reason
    job.save(update_fields=["status", "note", "updated_at"])
    maybe_auto_render(job.project_id)
    return job


def apply(job: FlowJob) -> None:
    """Put the result on the scene (a picture / clip you uploaded this way is never redrawn by the AI)."""
    data = Path(job.result.path).read_bytes()
    if job.kind == FlowJob.Kind.VIDEO:
        hook_video.save_uploaded(job.scene, _Upload(Path(job.result.name).name, data))
    else:
        manual_images.save_uploaded(job.scene, data)
    try:
        export_result(job)
    except OSError as exc:  # the copy is a convenience: never lose the result because of it
        logger.warning("Flow export copy failed for job %s: %s", job.pk, exc)
    Project.objects.filter(pk=job.project_id).update(has_unrendered_changes=True)


def requeue(job: FlowJob, reason: str) -> FlowJob:
    """A problem of the Flow page, not of this scene (settings, character, wrong page): back to the queue, try not counted."""
    job.status, job.attempts = FlowJob.Status.PENDING, max(0, job.attempts - 1)
    job.note = f"Kutmoqda: {(reason or '')[:300]}"
    job.save(update_fields=["status", "attempts", "note", "updated_at"])
    return job


def fail(job: FlowJob, error: str) -> FlowJob:
    """The extension could not make this one (Flow refused the prompt, timed out...)."""
    error = (error or "noma'lum xato")[:400]
    if job.attempts < settings.FLOW_MAX_ATTEMPTS:
        job.status, job.note = FlowJob.Status.PENDING, f"Qayta urinish: {error}"
    else:
        job.status, job.note = FlowJob.Status.FAILED, error
    job.save(update_fields=["status", "note", "updated_at"])
    maybe_auto_render(job.project_id)
    return job


def approve(job: FlowJob) -> None:
    """A human accepts a result the automatic check rejected."""
    if job.result:
        apply(job)
        job.status, job.note = FlowJob.Status.DONE, ""
        job.save(update_fields=["status", "note", "updated_at"])
        maybe_auto_render(job.project_id)


def retry(job: FlowJob) -> None:
    job.status, job.attempts, job.note = FlowJob.Status.PENDING, 0, ""
    job.save(update_fields=["status", "attempts", "note", "updated_at"])
