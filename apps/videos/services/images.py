"""Scene images: prompt building, generation through the configured provider,
and normalization of any image (AI-made or uploaded) to exactly 1920x1080."""
from __future__ import annotations

import io
import logging
import re
from typing import BinaryIO

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageOps

from .image_providers import ImageProvider, ImageProviderError, get_provider

logger = logging.getLogger(__name__)

TARGET_SIZE = (1920, 1080)
# Some FLUX endpoints return a square image that we crop to 16:9, so ask the model to
# keep whole bodies in the middle band with empty space above the heads.
COMPOSITION_HINT = ("wide 16:9 composition, characters drawn full body from head to feet in the middle of the frame, "
                    "plenty of empty sky or wall above their heads, nothing important near the top or bottom edge")
# Crop anchor for square -> 16:9: keep a bit more of the top (heads) than the bottom (ground).
CROP_CENTERING = (0.5, 0.35)
MAIN_CHARACTER_WORDS = re.compile(r"\b(the|our|a|same)\s+main\s+(character|hero|caveman|man)\b", re.I)
QA_ATTEMPTS = 2  # first image + at most one redraw when the vision check says the hero looks different


def normalize_to_1080p(src: BinaryIO | bytes, mode: str = "crop") -> bytes:
    """Return PNG bytes at 1920x1080.

    mode="crop": fill the frame, cutting the overflow (centre).
    mode="letterbox": fit inside the frame, padding with the image's edge colour.
    """
    data = src if isinstance(src, bytes) else src.read()
    img = Image.open(io.BytesIO(data))
    img = ImageOps.exif_transpose(img).convert("RGB")
    if mode == "letterbox":
        fitted = ImageOps.contain(img, TARGET_SIZE, Image.LANCZOS)
        bg_colour = fitted.getpixel((0, 0))
        canvas = Image.new("RGB", TARGET_SIZE, bg_colour)
        canvas.paste(fitted, ((TARGET_SIZE[0] - fitted.width) // 2, (TARGET_SIZE[1] - fitted.height) // 2))
        img = canvas
    else:
        img = ImageOps.fit(img, TARGET_SIZE, Image.LANCZOS, centering=CROP_CENTERING)
    out = io.BytesIO()
    img.save(out, "PNG", compress_level=6)  # optimize=True was ~3x slower for ~5% smaller files
    return out.getvalue()


def mentions_main_character(scene_prompt: str) -> bool:
    return bool(MAIN_CHARACTER_WORDS.search(scene_prompt or ""))


PEOPLE_WORDS = re.compile(r"\b(stick[- ]?figures?|people|persons?|figures?|group|crowd|children|child|kids?|friends?|elders?|"
                          r"scholars?|hunters?|families|family|listeners|silhouettes?|(?:cave)?m[ae]n|woman|women|"
                          r"neanderthals?(?! (?:skeleton|skull|bones?|tooth|teeth|jaw|femur|arm))|humans)\b", re.I)
OBJECT_COMPOSITION_HINT = ("wide 16:9 composition, the described object is large and centered in the frame with a simple "
                           "uncluttered background, nothing important near the edges")
OBJECT_ONLY_NOTE = "Only the described object and scenery, no people, no stick figures, no characters"
# hero scenes used to come out as the same pose (standing, facing the camera, a row of bystanders on each side)
STICK_HERO_NOTE = ("In every pose he stays a stick figure: round plain white head, thin black line arms and legs, "
                   "never a realistic body or skin-coloured limbs")
HERO_ACTION_NOTE = ("The main character is actively doing exactly what the scene describes, in a clear, expressive full-body pose "
                    "(side or three-quarter view when moving, sitting or lying down when the scene says so, hands busy with the "
                    "object), with a strong facial expression that fits the moment. Do not add other people or bystanders "
                    "unless the scene mentions them")
LIGHT_NOTE = ("Time of day, weather and light follow the scene: night is deep blue with warm firelight, rain and storms have "
              "dark grey skies and wet ground, dawn is soft pink; a sunny blue sky only when the scene is sunny")
CHARACTER_CLAUSE = re.compile(r"stick|character|face|limb|people|person", re.I)


def shows_people(scene_prompt: str) -> bool:
    return bool(PEOPLE_WORDS.search(scene_prompt or "")) or mentions_main_character(scene_prompt)


def object_style(style_guide: str) -> str:
    """The style guide without its stick-figure clauses, for pictures of objects, places and bones only."""
    clauses = [c.strip() for c in re.split(r"[;,]", style_guide) if c.strip()]
    return ", ".join(c for c in clauses if not CHARACTER_CLAUSE.search(c))


REALISTIC_NOTE = ("natural proportions, correct anatomy, realistic hands and faces, no text, no letters, no numbers, no logos, "
                  "no watermark, wide 16:9 composition")


def build_prompt(style_guide: str, scene_prompt: str, character: str = "", realistic: bool = False) -> str:
    """Final prompt = style guide + (character sheet) + scene content + composition hint.

    When the scene shows the main character, the full character sheet is inserted right
    before the scene and "the main character" is spelled out, so every image gets the same
    head, hair, clothes and colours instead of the model inventing a new person each time.
    """
    scene = scene_prompt.strip().rstrip(".")
    if realistic:  # photo-like niches (TeachAI): style + the scene, no character sheet, people allowed
        return ". ".join(p for p in (style_guide.strip().rstrip("."), f"Scene: {scene}" if scene else "", REALISTIC_NOTE) if p) + "."
    character = character.strip().rstrip(".")
    if scene and not shows_people(scene):  # bones, places, artefacts: the model must not add stick-figure crowds
        style = object_style(style_guide.strip().rstrip(".")) or style_guide.strip().rstrip(".")
        return ". ".join([style, f"Scene: {scene}", OBJECT_ONLY_NOTE, OBJECT_COMPOSITION_HINT]) + "."
    parts = [style_guide.strip().rstrip(".")]
    if character and mentions_main_character(scene):
        parts.append(f"MAIN CHARACTER (must look exactly the same in every image): {character}")
        scene = MAIN_CHARACTER_WORDS.sub("the main character (exactly as described above)", scene, count=1)
        parts.append(f"Scene: {scene}")
        parts.append("Draw the main character only once in this image, with the same face, hair and clothing")
        parts.append(HERO_ACTION_NOTE)
        if "stick" in (style_guide + character).lower():  # only the stickman style; anime/other heroes have real bodies
            parts.append(STICK_HERO_NOTE)
    else:
        parts.append(f"Scene: {scene}" if scene else "")
    parts.append(LIGHT_NOTE)
    parts.append(COMPOSITION_HINT)
    return ". ".join(p for p in parts if p) + "."


def character_reference_bytes(project) -> bytes | None:
    niche = getattr(project, "niche", None)
    ref = getattr(project, "character_reference_override", None)
    if not ref:
        ref = getattr(niche, "character_reference", None) if niche else None
    if not ref:
        return None
    try:
        with ref.open("rb") as fh:
            return fh.read()
    except (OSError, ValueError):
        logger.warning("Character reference image missing on disk")
        return None


def scene_seed(project_id: int, order: int) -> int:
    """Stable per-scene seed: regenerating gives a new picture only when the prompt changes
    (the 'force' path adds a salt)."""
    return project_id * 1000 + order


def needs_image(scene) -> bool:
    from .voice import file_missing

    missing = bool(scene.image) and file_missing(scene.image) and not scene.image_locked
    return (not scene.image or missing) and not scene.image_locked and bool(scene.image_prompt.strip())


class ImageJob:
    """Everything a worker thread needs to draw one scene without touching the database."""

    def __init__(self, scene, provider: ImageProvider, salt: int = 0):
        project = scene.project
        self.order = scene.order
        self.scene_prompt = scene.image_prompt
        self.character = project.character_description
        self.prompt = build_prompt(project.effective_style_guide, scene.image_prompt, self.character,
                                   realistic=bool(project.niche and project.niche.realistic))
        self.shows_hero = bool(self.character) and mentions_main_character(scene.image_prompt)
        self.reference = character_reference_bytes(project) if self.shows_hero else None
        self.refs = [self.reference] if self.reference and provider.supports_reference else None
        self.seed = scene_seed(scene.project_id, scene.order) + salt


def draw_image(job: ImageJob, provider: ImageProvider, qa: bool = True) -> tuple[bytes, str]:
    """Network part (thread-safe, no DB): generate + normalize (+ vision QA). Returns (png, qa_note)."""
    from .image_qa import check_scene_image

    png, note = b"", ""
    for attempt in range(QA_ATTEMPTS if qa else 1):
        png = normalize_to_1080p(provider.generate(job.prompt, seed=job.seed + attempt * 7919, references=job.refs),
                                 mode="crop")
        if not (qa and job.shows_hero):
            break
        result = check_scene_image(png, job.character, job.scene_prompt, job.reference)
        if result.ok:
            note = ""
            break
        note = result.reason
        logger.info("Scene %s image QA failed (%s), attempt %s", job.order, result.reason, attempt + 1)
    return png, note


def save_scene_image(scene, png: bytes, note: str = "", provider_name: str = "") -> None:
    from ..models import Scene

    if scene.image:
        scene.image.delete(save=False)
    scene.image.save("scene.png", ContentFile(png), save=False)
    scene.clip_hash = ""
    # A picture that still failed the check is kept (better than nothing) but flagged for the user.
    scene.error_message = f"Rasm tekshiruvi: {note}. '↻ Qayta chizish' ni bosing." if note else ""
    if scene.status == Scene.Status.FAILED:
        scene.status = Scene.Status.PENDING
    scene.save(update_fields=["image", "clip_hash", "error_message", "status"])
    logger.info("Image saved for project %s scene %s via %s", scene.project_id, scene.order, provider_name)


def generate_scene_image(scene, provider: ImageProvider | None = None, force: bool = False, salt: int = 0,
                         qa: bool = True) -> bool:
    """Generate and save one scene image. Returns True if a new image was saved.

    Never touches hand-uploaded (locked) images. Skips scenes that already have an
    image unless force=True. Raises ImageProviderError on failure.
    """
    if scene.image_locked:
        return False
    if scene.image and not force:
        return False
    if not scene.image_prompt.strip():
        raise ImageProviderError("Rasm tavsifi bo'sh — avval sahnaga rasm tavsifini yozing.")
    provider = provider or get_provider()
    png, note = draw_image(ImageJob(scene, provider, salt), provider, qa)
    save_scene_image(scene, png, note, provider.name)
    return True
