"""TTS provider interface (prompt 5.4)."""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from pathlib import Path


class TTSError(RuntimeError):
    """Safe-to-show error (Uzbek)."""


@dataclass
class WordTiming:
    word: str
    start: float  # seconds from the start of this scene's audio
    end: float


@dataclass
class TTSResult:
    path: Path
    duration: float
    word_timings: list[WordTiming] | None = field(default=None)


class TTSProvider(abc.ABC):
    name = "base"
    extension = ".mp3"
    supports_style = False  # True: synthesize() takes style=VoiceStyle (per-scene emotion / pace)

    @classmethod
    @abc.abstractmethod
    def from_settings(cls) -> "TTSProvider": ...

    @abc.abstractmethod
    def synthesize(self, text: str, out_path: Path) -> TTSResult:
        """Write audio for `text` to out_path (extension may be changed) and return the result."""
