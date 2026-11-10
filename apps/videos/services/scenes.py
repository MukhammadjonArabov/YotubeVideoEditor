"""Scene editing helpers used by the studio page: add / move / delete / edit.

All operations keep `Scene.order` contiguous (1..N) and flag the project as
having unrendered changes so the UI can offer a re-render.
"""
from __future__ import annotations

import logging

from django.db import transaction
from django.db.models import F

from ..models import Project, Scene

logger = logging.getLogger(__name__)

# Fields whose change makes the cached voice-over invalid / the cached clip invalid.
AUDIO_FIELDS = {"narration", "emotion", "intensity", "pace"}
CLIP_FIELDS = {"narration", "image_prompt", "beat_type", "sfx", "transition_in", "image", "camera_move",
               "on_screen_text", "music_cue", "pause_after_ms"}


def _mark_dirty(project: Project) -> None:
    Project.objects.filter(pk=project.pk).update(has_unrendered_changes=True)


def renumber(project: Project) -> None:
    """Make orders 1..N again (after a delete). Two passes avoid unique clashes."""
    scenes = list(project.scenes.order_by("order", "pk"))
    with transaction.atomic():
        for i, s in enumerate(scenes, start=1):
            Scene.objects.filter(pk=s.pk).update(order=10_000 + i)
        for i, s in enumerate(scenes, start=1):
            Scene.objects.filter(pk=s.pk).update(order=i)


@transaction.atomic
def add_scene(project: Project, after_order: int | None = None, **fields) -> Scene:
    """Insert a new scene after `after_order` (None = at the end)."""
    last = project.scenes.order_by("-order").values_list("order", flat=True).first() or 0
    if after_order is None or after_order >= last:
        new_order = last + 1
    else:
        new_order = max(after_order, 0) + 1
        # shift later scenes up by one; go through a high range to dodge the unique constraint
        later = project.scenes.filter(order__gte=new_order)
        later.update(order=F("order") + 10_000)
        project.scenes.filter(order__gte=10_000 + new_order).update(order=F("order") - 10_000 + 1)
    fields.setdefault("narration", "")
    scene = Scene.objects.create(project=project, order=new_order, **fields)
    _mark_dirty(project)
    return scene


@transaction.atomic
def move_scene(scene: Scene, direction: int) -> bool:
    """Swap with the neighbour above (-1) or below (+1). Returns False at the edges."""
    neighbour = Scene.objects.filter(project=scene.project, order=scene.order + direction).first()
    if not neighbour:
        return False
    a, b = scene.order, neighbour.order
    Scene.objects.filter(pk=scene.pk).update(order=999_999)  # temp slot (field is unsigned)
    Scene.objects.filter(pk=neighbour.pk).update(order=a)
    Scene.objects.filter(pk=scene.pk).update(order=b)
    scene.order = b
    # neighbours' transitions change position too -> both clips are stale
    Scene.objects.filter(pk__in=[scene.pk, neighbour.pk]).update(clip_hash="")
    _mark_dirty(scene.project)
    return True


def delete_scene(scene: Scene) -> None:
    project = scene.project
    for f in (scene.image, scene.audio, scene.clip):
        if f:
            f.delete(save=False)
    scene.delete()
    renumber(project)
    _mark_dirty(project)


def apply_scene_edit(scene: Scene, changed: set[str]) -> None:
    """Invalidate cached assets that depend on the changed fields, then save."""
    if changed & AUDIO_FIELDS:
        if scene.audio:
            scene.audio.delete(save=False)
        scene.audio = ""
        scene.audio_duration = None
        scene.subtitle_words = None
    if "image_prompt" in changed and not scene.image_locked and "image" not in changed:
        # prompt changed for an AI image -> regenerate it next time
        if scene.image:
            scene.image.delete(save=False)
        scene.image = ""
    if changed & CLIP_FIELDS:
        scene.clip_hash = ""
        scene.status = Scene.Status.PENDING
    scene.save()
    if changed:
        _mark_dirty(scene.project)
