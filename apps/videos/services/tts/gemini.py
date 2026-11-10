"""Gemini TTS (same API key as the rest of the app). No word timings -> they are found from the audio (faster-whisper).

The narrator is always a gentle, warm, soft-spoken documentary voice (never harsh or shouting, so a long video
doesn't tire the listener); each scene adds its own delivery from the director's emotion / intensity / pace:
audio tags in front of the line ([whispers], [excitedly]...) plus a plain-language note. A take that comes out
cut-off or stretched is made once more.
"""
from __future__ import annotations

import logging
import wave
from pathlib import Path

from django.conf import settings

from .base import TTSError, TTSProvider, TTSResult
from .elevenlabs import take_is_sane

logger = logging.getLogger(__name__)

DEFAULT_VOICE = "Algieba"  # smooth, calm male voice; others worth trying: Achernar (soft), Sulafat (warm), Schedar (even)
# emotion -> Gemini audio tag (bracketed, spoken as acting, not read aloud)
GEMINI_TAGS = {
    "neutral": "", "curious": "[curious]", "excited": "[excited]", "happy": "[warmly]", "funny": "[playfully]",
    "scared": "[nervous]", "tense": "[tense]", "sad": "[sadly]", "awe": "[in awe]", "whisper": "[softly]",
    "serious": "[serious]",
}
BASE_NOTE = ("Voice: a gentle, warm, soft-spoken documentary narrator. Smooth and unhurried, conversational, "
             "never harsh, never shouting, with natural short pauses. Keep the emotion subtle and believable, "
             "like a friendly storyteller by a fire.")


# TeachAI (Uzbek): a natural, sincere male teacher at a brisk conversational pace. The owner chose the voice "Umbriel" on 2026-10-24;
# with a "calm" note it spoke at ~1 word/s, so the note asks for a quick fluent pace and the take is gently time-corrected below.
UZ_NOTE = ("Voice: a natural, sincere, friendly adult male Uzbek teacher talking to a friend. Calm, relaxed and warm, with small smiles in "
           "the voice; not robotic, not announcer-like. Speak Uzbek (Latin script) with correct native Uzbek pronunciation. "
           "Speak at a brisk, lively conversational pace, like a confident teacher, with short natural pauses only at punctuation.")
UZ_WORDS_PER_SEC = (1.75, 2.15)  # Uzbek narration target (~105-130 words/min); takes outside it are sped up / slowed down slightly


class GeminiTTSProvider(TTSProvider):
    name = "gemini"
    extension = ".wav"
    supports_style = True

    def __init__(self, model: str, voice: str, base_note: str = BASE_NOTE, wps_range: tuple[float, float] | None = None):
        self.model = model
        self.voice = voice
        self.base_note = base_note
        self.wps_range = wps_range  # set for languages whose pace we normalise (Uzbek)

    @classmethod
    def from_settings(cls) -> "GeminiTTSProvider":
        if not settings.GEMINI_API_KEY.strip():
            raise TTSError(".env faylida GEMINI_API_KEY yo'q.")
        if not settings.GEMINI_TTS_MODEL.strip():
            raise TTSError(".env faylida GEMINI_TTS_MODEL yo'q (masalan gemini-3.8-flash-tts).")
        return cls(settings.GEMINI_TTS_MODEL.strip(), settings.GEMINI_TTS_VOICE.strip() or DEFAULT_VOICE)

    def build_prompt(self, text: str, style=None) -> str:
        tag = GEMINI_TAGS.get(style.emotion, "") if style else ""
        if style and style.intensity >= 3 and tag:
            tag += "[softly emphasized]"
        # "slow" / "fast" notes make this model drag or rush the whole line: only a light touch for fast, none for slow
        pace = " A touch brisker, still gentle." if getattr(style, "pace", "normal") == "fast" and not self.wps_range else ""
        mood = style.gemini_words() if style else "warm, curious"
        mood = mood.replace(", unhurried", "") if self.wps_range else mood  # the Uzbek voice already runs slow
        return (f"{self.base_note} Delivery for this line: {mood}.{pace}\n"
                f"Read ONLY the transcript below aloud, not these notes.\n\nTRANSCRIPT:\n{tag} {text}".strip())

    def _one_take(self, text: str, style) -> bytes:
        from google.genai import types

        from .. import gemini_client

        client = gemini_client.get_client()
        cfg = types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=self.voice))),
        )
        prompt = self.build_prompt(text, style)
        try:
            resp = gemini_client._call(lambda: client.models.generate_content(model=self.model, contents=prompt, config=cfg),
                                       "gemini_tts")
            return resp.candidates[0].content.parts[0].inline_data.data
        except (gemini_client.GeminiError, AttributeError, IndexError, TypeError) as exc:
            raise TTSError(f"Gemini TTS ishlamadi: {str(exc)[:200]}") from exc

    def synthesize(self, text: str, out_path: Path, style=None) -> TTSResult:
        out_path = Path(out_path).with_suffix(self.extension)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        pcm, duration = b"", 0.0
        for attempt in (1, 2):
            pcm = self._one_take(text.strip(), style)
            duration = len(pcm) / 2 / 24000  # 24 kHz, 16-bit mono
            if take_is_sane(text, duration) or attempt == 2:
                if attempt == 2 and not take_is_sane(text, duration):
                    logger.warning("Gemini TTS take still odd after retry (%.1fs for %d words)", duration, len(text.split()))
                break
            logger.info("Gemini TTS take looked wrong (%.1fs for %d words) - retrying once", duration, len(text.split()))
        with wave.open(str(out_path), "wb") as w:  # Gemini returns 24 kHz 16-bit mono PCM
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(24000)
            w.writeframes(pcm)
        if self.wps_range and len(text.split()) >= 4:
            duration = self._normalise_pace(out_path, text, duration)
        return TTSResult(out_path, round(duration, 3), None)

    def _normalise_pace(self, path: Path, text: str, duration: float) -> float:
        """Speed a too-slow take up (or slow a too-fast one down) with ffmpeg atempo so the video length stays predictable."""
        import subprocess

        from ..render import ffmpeg_exe

        lo, hi = self.wps_range
        rate = len(text.split()) / max(duration, 0.01)
        factor = lo / rate if rate < lo else hi / rate if rate > hi else 1.0
        factor = min(max(factor, 0.85), 1.5)
        if abs(factor - 1.0) < 0.04:
            return duration
        tmp = path.with_name(path.stem + "_tempo.wav")
        proc = subprocess.run([ffmpeg_exe(), "-y", "-v", "error", "-i", str(path), "-filter:a", f"atempo={factor:.3f}", str(tmp)],
                              capture_output=True)
        if proc.returncode != 0 or not tmp.exists():
            logger.warning("atempo failed: %s", proc.stderr[-200:])
            return duration
        tmp.replace(path)
        with wave.open(str(path), "rb") as w:
            return w.getnframes() / w.getframerate()
