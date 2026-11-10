"""Microsoft Edge online TTS via the `edge-tts` package (free, gives word boundaries)."""
from __future__ import annotations

import asyncio
import logging
import time
from pathlib import Path

from django.conf import settings

from .base import TTSError, TTSProvider, TTSResult, WordTiming

logger = logging.getLogger(__name__)
TICKS = 10_000_000  # edge-tts offsets are in 100-ns units

EDGE_TIMEOUT_SEC = 60


class EdgeTTSProvider(TTSProvider):
    name = "edge"
    extension = ".mp3"
    supports_style = True

    # pause before attempt 2 and 3: short network / DNS hiccups usually pass in a few seconds
    retry_delays = (3, 8)

    def __init__(self, voice: str, rate: str = "+0%"):
        self.voice = voice
        self.rate = rate

    @classmethod
    def from_settings(cls) -> "EdgeTTSProvider":
        return cls(settings.EDGE_TTS_VOICE or "en-US-AndrewMultilingualNeural", getattr(settings, "EDGE_TTS_RATE", "+0%"))

    async def _run(self, text: str, out_path: Path, prosody: dict | None = None) -> list[WordTiming]:
        import aiohttp
        import edge_tts

        # Windows: use the operating system's DNS resolver (ThreadedResolver). The async
        # c-ares resolver aiohttp picks when `aiodns` is installed often fails there with
        # ClientConnectorDNSError even though the internet works.
        connector = aiohttp.TCPConnector(resolver=aiohttp.ThreadedResolver())
        prosody = prosody or {"rate": self.rate}
        comm = edge_tts.Communicate(text, self.voice, boundary="WordBoundary", connector=connector, **prosody)
        words: list[WordTiming] = []
        with open(out_path, "wb") as fh:
            async for chunk in comm.stream():
                if chunk["type"] == "audio":
                    fh.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    start = chunk["offset"] / TICKS
                    words.append(WordTiming(chunk["text"], round(start, 3), round(start + chunk["duration"] / TICKS, 3)))
        return words

    def synthesize(self, text: str, out_path: Path, style=None) -> TTSResult:
        from ..autoinstall import ensure_module
        from ..media_library import audio_duration

        if not ensure_module("edge_tts", "edge-tts==7.3.1"):
            raise TTSError("edge-tts paketi o'rnatilmagan va avtomatik o'rnatib bo'lmadi. Terminalda: "
                           "pip install -r requirements.txt, keyin python manage.py dev ni qayta ishga tushiring.")

        out_path = Path(out_path).with_suffix(self.extension)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        last = None
        for attempt in range(1, 4):
            try:
                # a stalled connection used to hang the whole voice stage forever (2026-10-26)
                words = asyncio.run(asyncio.wait_for(self._run(text, out_path, style.edge_params(self.rate) if style else None),
                                                     timeout=EDGE_TIMEOUT_SEC))
                if out_path.stat().st_size == 0:
                    raise TTSError("bo'sh audio qaytdi")
                break
            except Exception as exc:  # noqa: BLE001 - network hiccups are common
                last = exc
                logger.warning("edge-tts failed (attempt %s): %s", attempt, exc.__class__.__name__)
                if attempt <= len(self.retry_delays):
                    time.sleep(self.retry_delays[attempt - 1])
        else:
            name = last.__class__.__name__
            hint = ("Internet yoki DNS vaqtincha ishlamadi — bir daqiqadan keyin qayta bosing."
                    if "DNS" in name or "Connect" in name or "Timeout" in name else "Internetni tekshiring.")
            raise TTSError(f"Edge TTS ishlamadi ({name}: {str(last)[:150]}). {hint}")
        duration = audio_duration(out_path) or (words[-1].end if words else 0.0)
        return TTSResult(out_path, duration, words or None)
