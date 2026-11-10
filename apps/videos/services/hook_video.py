"""Moving pictures for the hook. The first ~12 scenes (beat_type "hook") can be real video clips made in
Google Flow (Veo, "Frames to video": the scene's picture is the start frame, so the hero looks the same).
The rest of the film stays pictures with camera moves, transitions and sound effects.

Flow clips are ~8 s; a hook line lasts 2-3 s, so the render uses the first seconds of each clip. Veo's own
sound is dropped: the narration, music and SFX of this app are the only audio.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import PurePath

from django.core.files.base import ContentFile

from .manual_images import natural_key, number_from_name

VIDEO_EXT = {".mp4", ".mov", ".webm", ".m4v"}
MOTION_HINT = ("hand-drawn 2D animation of this exact picture, the characters and objects move naturally, "
               "gentle camera push-in, keep the same drawing style and colours, no text, no letters, "
               "no speech, no music, 16:9")


def hook_scenes(project) -> list:
    return [s for s in project.scenes.order_by("order") if s.beat_type == "hook"]


def video_prompt(scene) -> str:
    """Motion prompt for Flow's Frames-to-video. Picture first (it is the start frame), then what moves."""
    base = (scene.image_prompt or f"illustration of: {scene.narration.strip()}").strip().rstrip(".")
    base = re.sub(r"\bthe main character\b", "the character", base, flags=re.I)
    return " ".join(f"{base}. {MOTION_HINT}.".split())


def prompt_rows(project) -> list[tuple[int, str]]:
    return [(s.order, video_prompt(s)) for s in hook_scenes(project)]


def prompts_txt(project, numbered: bool = False, spaced: bool = False) -> str:
    """spaced=True puts an empty line between prompts (easier to read)."""
    rows = prompt_rows(project)
    sep = "\n\n" if spaced else "\n"
    if numbered:
        return sep.join(f"{o:03d} | {p}" for o, p in rows) + "\n"
    return sep.join(p for _, p in rows) + "\n"


@dataclass
class VideoMatch:
    assigned: dict[str, int] = field(default_factory=dict)  # file name -> scene order
    unmatched: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)  # not videos


def match_files(names: list[str], scenes, mode: str = "auto", start: int = 1) -> VideoMatch:
    """Only hook scenes take videos. auto = scene number in the file name; order = natural file order."""
    hook = sorted((s for s in scenes if s.beat_type == "hook"), key=lambda s: s.order)
    res = VideoMatch()
    vids = []
    for n in names:
        (vids if PurePath(n).suffix.lower() in VIDEO_EXT else res.skipped).append(n)
    vids.sort(key=natural_key)
    if mode == "order":
        targets = [s.order for s in hook if s.order >= start]
        for name, order in zip(vids, targets):
            res.assigned[name] = order
        res.unmatched = vids[len(targets):]
        return res
    valid = {s.order for s in hook}
    taken: set[int] = set()
    for name in vids:
        order = number_from_name(name, valid)
        if order is not None and order not in taken:
            res.assigned[name] = order
            taken.add(order)
    res.unmatched = [n for n in vids if n not in res.assigned]
    return res


def save_uploaded(scene, upload) -> None:
    from ..models import Scene

    ext = PurePath(upload.name).suffix.lower() or ".mp4"
    if scene.video:
        scene.video.delete(save=False)
    scene.video.save(f"scene{ext}", ContentFile(upload.read()), save=False)
    scene.clip_hash = ""
    scene.error_message = ""
    if scene.status == Scene.Status.FAILED:
        scene.status = Scene.Status.PENDING
    scene.save(update_fields=["video", "clip_hash", "status", "error_message"])
