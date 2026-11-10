"""ElevenLabs TTS (paid, optional). Uses the /with-timestamps endpoint to get word timings.

eleven_v3 (default) is told how to *act* each line with audio tags in front of the text ("[whispers] They
were not alone."), chosen from the scene's emotion / intensity / pace (see voice_style.ELEVEN_TAGS).
eleven_multilingual_v2 has no tags, so there the same direction becomes voice_settings (stability,
style, speed). The tags are spoken as acting, not read aloud, and are removed from the word timings.
"""
from __future__ import annotations

import base64
import logging
from pathlib import Path

import requests
from django.conf import settings

from .base import TTSError, TTSProvider, TTSResult, WordTiming

logger = logging.getLogger(__name__)

URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps"
DEFAULT_VOICE = "nPczCjzI2devNBz1zQrb"  # Brian: deep, warm documentary narrator (premade, works on every plan)
WORDS_PER_SEC = (1.2, 4.6)  # outside this a take is cut off or garbled -> one automatic retry


def words_from_alignment(chars: list[str], starts: list[float], ends: list[float]) -> list[WordTiming]:
    """Character timings -> word timings. Anything inside [square brackets] (v3 audio tags) is skipped."""
    words: list[WordTiming] = []
    cur, s, prev_end, depth = "", None, 0.0, 0
    for ch, a, b in zip(chars, starts, ends):
        if ch == "[":
            depth += 1
            continue
        if depth:
            depth -= ch == "]"
            continue
        if ch.isspace():
            if cur:
                words.append(WordTiming(cur, round(s, 3), round(prev_end, 3)))
            cur, s = "", None
            continue
        if s is None:
            s = a
        cur += ch
        prev_end = b
    if cur:
        words.append(WordTiming(cur, round(s, 3), round(prev_end, 3)))
    return words


def take_is_sane(text: str, duration: float) -> bool:
    n = len(text.split())
    if n < 4:  # too short to judge
        return duration > 0.3
    rate = n / max(duration, 0.01)
    return WORDS_PER_SEC[0] <= rate <= WORDS_PER_SEC[1]


class ElevenLabsProvider(TTSProvider):
    name = "elevenlabs"
    extension = ".mp3"
    supports_style = True

    def __init__(self, api_key: str, voice_id: str, model: str = "eleven_v3"):
        self.api_key = api_key
        self.voice_id = voice_id
        self.model = model

    @classmethod
    def from_settings(cls) -> "ElevenLabsProvider":
        if not settings.ELEVENLABS_API_KEY.strip():
            raise TTSError(".env faylida ELEVENLABS_API_KEY kerak.")
        return cls(settings.ELEVENLABS_API_KEY.strip(), settings.ELEVENLABS_VOICE_ID.strip() or DEFAULT_VOICE,
                   (getattr(settings, "ELEVENLABS_MODEL", "") or "eleven_v3").strip())

    # ---- how the line is acted
    def request_body(self, text: str, style=None) -> dict:
        text = text.strip()
        if self.model == "eleven_v3":
            tags = style.eleven_tags() if style else ""
            # v3 stability is 0 (creative) / 0.5 (natural) / 1 (robust): natural keeps one voice, tags still act
            return {"text": f"{tags} {text}".strip(), "model_id": self.model, "voice_settings": {"stability": 0.5}}
        emotion = style.emotion if style else "neutral"
        calm = emotion in ("neutral", "serious", "sad", "whisper", "tense", "scared", "awe")
        rate = style.offsets()[0] if style else 0
        return {"text": text, "model_id": self.model, "voice_settings": {
            "stability": 0.55 if calm else 0.35, "similarity_boost": 0.8, "style": 0.1 if calm else 0.4,
            "use_speaker_boost": True, "speed": round(min(1.2, max(0.8, 1 + rate / 100)), 2)}}

    def _request(self, text: str, style) -> dict:
        try:
            r = requests.post(URL.format(voice=self.voice_id), headers={"xi-api-key": self.api_key},
                              json=self.request_body(text, style), timeout=120)
        except requests.RequestException as exc:
            raise TTSError(f"ElevenLabs bilan aloqa xatosi: {exc.__class__.__name__}") from exc
        if r.status_code != 200:
            raise TTSError(f"ElevenLabs xatosi {r.status_code}: {r.text[:200]}")
        return r.json()

    def synthesize(self, text: str, out_path: Path, style=None) -> TTSResult:
        from ..media_library import audio_duration

        out_path = Path(out_path).with_suffix(self.extension)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        for attempt in (1, 2):
            data = self._request(text, style)
            out_path.write_bytes(base64.b64decode(data["audio_base64"]))
            al = data.get("alignment") or {}
            words = words_from_alignment(al.get("characters", []), al.get("character_start_times_seconds", []),
                                         al.get("character_end_times_seconds", []))
            duration = audio_duration(out_path) or (words[-1].end if words else 0)
            if take_is_sane(text, duration) or attempt == 2:
                if attempt == 2 and not take_is_sane(text, duration):
                    logger.warning("ElevenLabs take still odd after retry (%.1fs for %d words)", duration, len(text.split()))
                return TTSResult(out_path, duration, words or None)
            logger.info("ElevenLabs take looked wrong (%.1fs for %d words) - retrying once", duration, len(text.split()))
        raise TTSError("ElevenLabs ovozi yaratilmadi.")  # unreachable
