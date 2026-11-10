"""Per-scene voice-over generation (prompt 5.4)."""
from __future__ import annotations

import logging
import tempfile
from dataclasses import asdict
from pathlib import Path

from django.core.files import File

from .tts import TTSProvider, TTSResult, get_tts
from .voice_style import VoiceStyle

logger = logging.getLogger(__name__)


def file_missing(field) -> bool:
    """The database names a file that is no longer on disk (deleted, moved): it must be made again."""
    try:
        return not Path(field.path).exists()
    except (ValueError, NotImplementedError, OSError):
        return False


def needs_audio(scene) -> bool:
    return bool(scene.narration.strip()) and (not scene.audio or file_missing(scene.audio))


def synthesize(order: int, text: str, provider: TTSProvider, folder: Path, style=None) -> TTSResult:
    """Network part (thread-safe, no DB): write the voice-over for one scene into `folder`.
    `style` (VoiceStyle) changes the delivery per scene when the provider supports it."""
    out = Path(folder) / f"scene_{order:03d}{provider.extension}"
    if style is not None and getattr(provider, "supports_style", False):
        return provider.synthesize(text.strip(), out, style=style)
    return provider.synthesize(text.strip(), out)


def _align_words(path: Path, text: str, duration: float) -> list[dict] | None:
    """Word timings from the audio (faster-whisper) for voices that don't return them. Never fails."""
    from . import align

    if not align.enabled():
        return None
    try:
        return align.align(path, text, duration)
    except Exception as exc:  # noqa: BLE001 - captions fall back to proportional timing
        logger.warning("Word alignment skipped: %s", str(exc)[:200])
        return None


def save_scene_audio(scene, result: TTSResult) -> None:
    """Store a synthesized voice-over on the scene (+ duration, word timings)."""
    from ..models import Scene

    if scene.audio:
        scene.audio.delete(save=False)
    with open(result.path, "rb") as fh:
        scene.audio.save(f"scene{result.path.suffix}", File(fh), save=False)
    scene.audio_duration = round(result.duration, 3)
    scene.subtitle_words = [asdict(w) for w in result.word_timings] if result.word_timings else None
    if scene.subtitle_words is None:
        scene.subtitle_words = _align_words(result.path, scene.narration, result.duration)
    scene.clip_hash = ""
    if scene.status == Scene.Status.FAILED:
        scene.status = Scene.Status.PENDING
    if not scene.error_message.startswith("Rasm tekshiruvi"):  # keep the image QA warning
        scene.error_message = ""
    scene.save(update_fields=["audio", "audio_duration", "subtitle_words", "clip_hash", "status", "error_message"])


def generate_scene_audio(scene, provider: TTSProvider | None = None, force: bool = False) -> bool:
    """Synthesize narration -> scene.audio (+ duration, word timings). Returns True if new audio was saved."""
    if not scene.narration.strip():
        return False
    if scene.audio and not force:
        return False
    provider = provider or get_tts(scene.project.tts_provider, scene.project)
    with tempfile.TemporaryDirectory() as tmp:
        save_scene_audio(scene, synthesize(scene.order, scene.narration, provider, Path(tmp),
                                           VoiceStyle.for_scene(scene)))
    return True
