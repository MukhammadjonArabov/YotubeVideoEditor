"""Pluggable TTS: switch with TTS_PROVIDER in .env or per project in the UI."""
from __future__ import annotations

from .base import TTSError, TTSProvider, TTSResult, WordTiming
from .edge import EdgeTTSProvider
from .elevenlabs import ElevenLabsProvider
from .gemini import GeminiTTSProvider

PROVIDERS: dict[str, type[TTSProvider]] = {
    "edge": EdgeTTSProvider,
    "gemini": GeminiTTSProvider,
    "elevenlabs": ElevenLabsProvider,
}


def get_tts(name: str, project=None) -> TTSProvider:
    cls = PROVIDERS.get((name or "edge").lower())
    if cls is None:
        raise TTSError(f"Noma'lum ovoz provayderi: {name}")
    provider = cls.from_settings()
    niche = getattr(project, "niche", None) if project is not None else None
    voice = (niche.tts_voice or "").strip() if niche is not None else ""
    if voice.lower().startswith("gemini:"):  # e.g. "gemini:Umbriel" (TeachAI): Gemini TTS with that voice, whatever the project says
        from .gemini import UZ_NOTE, UZ_WORDS_PER_SEC

        provider = GeminiTTSProvider.from_settings()
        provider.voice = voice.split(":", 1)[1].strip() or provider.voice
        if niche.language == "uz":
            provider.base_note, provider.wps_range = UZ_NOTE, UZ_WORDS_PER_SEC
        return provider
    if voice.lower().startswith("navoiy:"):  # whole projects go through tts/navoiy.py; single lines fall back to Edge
        provider = EdgeTTSProvider.from_settings()
        provider.voice = "uz-UZ-SardorNeural"
        return provider
    if niche is not None and niche.tts_voice and isinstance(provider, EdgeTTSProvider):  # e.g. an Uzbek voice for TeachAI
        provider.voice = niche.tts_voice
    return provider


__all__ = ["TTSError", "TTSProvider", "TTSResult", "WordTiming", "get_tts", "PROVIDERS"]
