"""Hand-made images (e.g. drawn in Google Flow): export the prompts, then bulk-upload
the pictures and match every file to its scene.

Matching (mode="auto"):
  1. a zero-padded scene number in the file name: 001.png, scene_012.jpg, img-07.png
  2. a plain number in the file name that is a valid scene number: "image (12).png"
  3. the file name looks like the start of a prompt (bulk extensions often name files that way)
mode="order": files sorted by name (1, 2, 10 - natural order) go to scenes from `start` onward.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import PurePath

from django.core.files.base import ContentFile

from .images import COMPOSITION_HINT, MAIN_CHARACTER_WORDS, normalize_to_1080p

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
PADDED = re.compile(r"(?<!\d)0\d{1,3}(?!\d)")
NUMBER = re.compile(r"(?<!\d)\d{1,4}(?!\d)")
# dates and clock times in download names ("2026-09-27", "18_42_05") are not scene numbers
DATE_TIME = re.compile(r"(?<!\d)(\d{4}[-_. ]?\d{2}[-_. ]?\d{2}|\d{1,2}[-_.:]\d{2}[-_.:]\d{2})(?!\d)")
FLOW_HINT = "16:9 widescreen image, no text, no letters, no watermark"


NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]*(_[A-Za-z0-9]+)+$")


def clean_character_name(name: str) -> str:
    """Flow asset name used by bulk extensions ("underscore_names"), e.g. main_hero."""
    name = (name or "").strip().replace(" ", "_")
    return name if NAME_RE.match(name) else ""


def flow_prompt(project, scene, character_name: str = "") -> str:
    """One-line prompt for Flow. The scene comes FIRST, so downloaded file names (which
    extensions build from the prompt start) differ from scene to scene.

    character_name (e.g. main_hero): the extension attaches that Flow character asset as a
    reference, so the long text description is replaced by the name.
    """
    scene_text = (scene.image_prompt or "").strip() or f"illustration of: {scene.narration.strip()}"
    scene_text = scene_text.rstrip(".")
    parts = []
    if character_name and MAIN_CHARACTER_WORDS.search(scene_text):
        parts.append(MAIN_CHARACTER_WORDS.sub(character_name, scene_text))
        parts.append(f"{character_name} must look exactly like the {character_name} reference")
    elif project.character_description and MAIN_CHARACTER_WORDS.search(scene_text):
        parts.append(scene_text)
        parts.append(f"The main character (must look exactly the same in every image): "
                     f"{project.character_description.strip().rstrip('.')}")
    else:
        parts.append(scene_text)
    parts += [f"Style: {project.effective_style_guide.strip().rstrip('.')}", COMPOSITION_HINT, FLOW_HINT]
    return " ".join((". ".join(p for p in parts if p) + ".").split())


def prompt_rows(project, character_name: str = "") -> list[tuple[int, str]]:
    """Every scene gets a line (queue position = scene number), even one without an image prompt."""
    return [(s.order, flow_prompt(project, s, character_name)) for s in project.scenes.order_by("order")]


def prompts_txt(project, numbered: bool = False, character_name: str = "", spaced: bool = False) -> str:
    """spaced=True puts an empty line between prompts (easier to read); bulk-prompt extensions want one per line."""
    rows = prompt_rows(project, character_name)
    sep = "\n\n" if spaced else "\n"
    if numbered:
        return sep.join(f"{o:03d} | {p}" for o, p in rows) + "\n"
    return sep.join(p for _, p in rows) + "\n"


def natural_key(name: str):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]


def _slug(text: str) -> str:
    return " ".join(re.findall(r"[a-z]+", text.lower()))


def number_from_name(name: str, valid: set[int]) -> int | None:
    raw = PurePath(name).stem
    lead = re.match(r"\s*(\d{1,4})(?!\d)", raw)  # "7_the main character ....png" (queue position prefix)
    if lead and int(lead.group(1)) in valid:
        return int(lead.group(1))
    stem = DATE_TIME.sub(" ", raw)
    padded = [int(m) for m in PADDED.findall(stem) if int(m) in valid]
    if len(set(padded)) == 1:
        return padded[0]
    plain = [int(m) for m in NUMBER.findall(stem) if int(m) in valid]
    if len(set(plain)) == 1:
        return plain[0]
    if plain and not padded:
        return plain[-1]  # "Flow 2026 09 27 image 12" -> the last one is usually the counter
    return None


def prompt_match(name: str, scenes) -> int | None:
    """File named after the prompt start -> the scene whose image prompt starts the same way.
    Needs a clear winner, otherwise None (never guess between two similar scenes)."""
    words = _slug(re.sub(r"^\s*\d+", "", PurePath(name).stem))
    if len(words.split()) < 4:
        return None
    scored = []
    for s in scenes:
        target = _slug(s.image_prompt or s.narration)
        target = MAIN_CHARACTER_WORDS.sub("", target)
        cand = [_slug(s.image_prompt or s.narration)[: len(words) + 10], target[: len(words) + 10]]
        scored.append((max(SequenceMatcher(None, words, c).ratio() for c in cand), s.order))
    scored.sort(reverse=True)
    if not scored or scored[0][0] < 0.8:
        return None
    if len(scored) > 1 and scored[0][0] - scored[1][0] < 0.1:
        return None
    return scored[0][1]


@dataclass
class MatchResult:
    assigned: dict[str, int] = field(default_factory=dict)  # file name -> scene order
    unmatched: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)  # not images


def match_files(names: list[str], scenes, mode: str = "auto", start: int = 1) -> MatchResult:
    scenes = sorted(scenes, key=lambda s: s.order)
    res = MatchResult()
    images = []
    for n in names:
        (images if PurePath(n).suffix.lower() in IMAGE_EXT else res.skipped).append(n)
    if mode == "order":
        targets = [s.order for s in scenes if s.order >= start]
        ordered = sorted(images, key=natural_key)
        for name, order in zip(ordered, targets):
            res.assigned[name] = order
        res.unmatched = ordered[len(targets):]
        return res
    valid = {s.order for s in scenes}
    taken: set[int] = set()
    # pass 1: scene / queue number in the name (extensions number their downloads),
    # pass 2: names that spell out the start of a prompt
    for finder in (lambda n: number_from_name(n, valid), lambda n: prompt_match(n, scenes)):
        for name in sorted(images, key=natural_key):
            if name in res.assigned:
                continue
            order = finder(name)
            if order is not None and order not in taken:
                res.assigned[name] = order
                taken.add(order)
    res.unmatched = [n for n in sorted(images, key=natural_key) if n not in res.assigned]
    return res


def save_uploaded(scene, upload) -> None:
    from ..models import Scene

    png = normalize_to_1080p(upload, mode="crop")
    if scene.image:
        scene.image.delete(save=False)
    scene.image.save("scene.png", ContentFile(png), save=False)
    scene.image_locked = True  # the AI never overwrites a hand-made picture
    scene.clip_hash = ""
    scene.error_message = ""
    if scene.status == Scene.Status.FAILED:
        scene.status = Scene.Status.PENDING
    scene.save(update_fields=["image", "image_locked", "clip_hash", "error_message", "status"])
