"""Vision check of a freshly drawn scene image (Gemini): is the main character the
same one as in the character bible / reference, and is nobody's head cut off?

Non-blocking: if Gemini is not configured or fails, the image is accepted."""
from __future__ import annotations

import io
import logging
from dataclasses import dataclass

from PIL import Image
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class QAOut(BaseModel):
    main_character_present: bool = Field(description="Is the main character visible in the image?")
    matches_character: bool = Field(description="If present: does he match the description (and reference) exactly?")
    heads_cut_off: bool = Field(description="Is any character's head cut off by the image border?")
    problems: str = Field(default="", description="Short list of what differs from the character sheet, or empty")


@dataclass
class QAResult:
    ok: bool
    reason: str = ""
    checked: bool = True


def _small_jpeg(data: bytes, max_side: int = 768) -> bytes:
    img = Image.open(io.BytesIO(data)).convert("RGB")
    img.thumbnail((max_side, max_side))
    out = io.BytesIO()
    img.save(out, "JPEG", quality=85)
    return out.getvalue()


def build_qa_prompt(character: str, scene_prompt: str, has_reference: bool) -> str:
    ref = ("The FIRST image is the official reference drawing of the main character; the SECOND image is the new scene. "
           if has_reference else "The image is a new scene from an animated explainer video. ")
    return (
        f"{ref}Main character sheet: {character}\n"
        f"The scene was supposed to show: {scene_prompt}\n\n"
        "Judge strictly but only on identity, not on art quality: head shape and colour, face style, hair, "
        "beard (or lack of it), clothing and its colour must match the sheet. Other background people may differ. "
        "If the scene does not need the main character and he is absent, set main_character_present=false. "
        "Also report whether any character's head is cut off by the top or side edge."
    )


def check_scene_image(png: bytes, character: str, scene_prompt: str, reference: bytes | None = None) -> QAResult:
    from . import gemini_client

    if not character.strip() or not gemini_client.is_configured():
        return QAResult(True, checked=False)
    images = ([_small_jpeg(reference)] if reference else []) + [_small_jpeg(png)]
    try:
        out = gemini_client.generate_json(build_qa_prompt(character, scene_prompt, bool(reference)), QAOut,
                                          temperature=0.1, images=images, max_retries=2)
    except Exception as exc:  # noqa: BLE001 - QA must never stop image generation
        logger.warning("Image QA skipped: %s", str(exc)[:200])
        return QAResult(True, checked=False)
    problems = []
    if out.heads_cut_off:
        problems.append("bosh kesilib qolgan")
    if out.main_character_present and not out.matches_character:
        problems.append("qahramon boshqacha" + (f": {out.problems[:160]}" if out.problems else ""))
    return QAResult(not problems, "; ".join(problems))
