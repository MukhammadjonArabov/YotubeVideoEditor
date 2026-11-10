"""Word timings from the audio itself (faster-whisper), for voices that don't return them
(ElevenLabs v3, Gemini TTS, local voice clones). Edge TTS gives timings, so this is skipped there.

The words shown in the captions always come from the script; Whisper only supplies *when* each
word is spoken. Script words are matched to Whisper's words in order (difflib), and words Whisper
missed get times interpolated from their neighbours.

Windows note: faster-whisper imports PyAV, whose DLL can be blocked by Smart App Control. PyAV is
only used for decoding audio files, so it is stubbed out and audio is decoded with ffmpeg instead.
"""
from __future__ import annotations

import difflib
import logging
import re
import subprocess
import sys
import threading
import types
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)
SAMPLE_RATE = 16000
_model = None
_lock = threading.Lock()


class AlignError(RuntimeError):
    pass


def enabled() -> bool:
    return bool(getattr(settings, "ALIGN_MISSING_TIMINGS", True))


def _norm(word: str) -> str:
    return re.sub(r"[^a-z0-9']", "", word.lower().replace("’", "'"))


def _load_model():
    global _model
    with _lock:
        if _model is None:
            sys.modules.setdefault("av", types.ModuleType("av"))  # see module docstring
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                raise AlignError("faster-whisper o'rnatilmagan: pip install -r requirements.txt") from exc
            _model = WhisperModel(getattr(settings, "WHISPER_MODEL", "base.en"), device="cpu", compute_type="int8")
        return _model


def _decode(path: Path):
    import numpy as np

    from .render import ffmpeg_exe

    proc = subprocess.run([ffmpeg_exe(), "-v", "error", "-i", str(path), "-f", "s16le", "-ac", "1",
                           "-ar", str(SAMPLE_RATE), "-"], capture_output=True)
    if proc.returncode != 0:
        raise AlignError(f"Audio o'qilmadi: {proc.stderr[-300:]!r}")
    return np.frombuffer(proc.stdout, np.int16).astype(np.float32) / 32768


def transcribe_words(path: Path) -> list[tuple[str, float, float]]:
    """(word, start, end) as heard by Whisper."""
    audio = _decode(path)  # first: a broken file fails fast, before the ~20 s model load
    segments, _ = _load_model().transcribe(audio, language="en", word_timestamps=True, beam_size=1,
                                   vad_filter=False, condition_on_previous_text=False)
    return [(w.word.strip(), float(w.start), float(w.end)) for s in segments for w in (s.words or [])]


def map_to_script(script_text: str, heard: list[tuple[str, float, float]], duration: float) -> list[dict]:
    """Give every script word a (start, end), using Whisper's matched words and interpolating the rest."""
    words = script_text.split()
    if not words:
        return []
    times: list[tuple[float, float] | None] = [None] * len(words)
    matcher = difflib.SequenceMatcher(a=[_norm(w) for w in words], b=[_norm(w) for w, _, _ in heard], autojunk=False)
    for block in matcher.get_matching_blocks():
        for k in range(block.size):
            _, s, e = heard[block.b + k]
            times[block.a + k] = (s, e)
    # fill gaps between known anchors (or the clip edges) proportionally to word length
    i = 0
    while i < len(words):
        if times[i] is not None:
            i += 1
            continue
        j = i
        while j < len(words) and times[j] is None:
            j += 1
        left = times[i - 1][1] if i > 0 else 0.0
        right = times[j][0] if j < len(words) else max(duration, left)
        weights = [len(words[k]) + 2 for k in range(i, j)]
        span, t = max(0.0, right - left), left
        for k, wt in zip(range(i, j), weights):
            d = span * wt / sum(weights)
            times[k] = (t, t + d)
            t += d
        i = j
    return [{"word": w, "start": round(s, 3), "end": round(max(e, s + 0.05), 3)} for w, (s, e) in zip(words, times)]


def align(path: Path, script_text: str, duration: float) -> list[dict]:
    return map_to_script(script_text, transcribe_words(Path(path)), duration)
