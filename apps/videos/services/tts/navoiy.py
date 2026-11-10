"""Local Uzbek voice (Navoiy TTS = CosyVoice2 + aisha-org/navoiy-tts) cloned from the owner's own recording.

It lives in its own Python on D: (D:\\AI\\navoiy-tts) and is slow on this CPU (~20x real time), so a whole project is
voiced in one batch job (one model load) instead of scene by scene. A niche uses it with tts_voice "navoiy:<prompt name>",
e.g. "navoiy:men" -> D:\\AI\\navoiy-tts\\namuna\\men.wav.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .base import TTSError, TTSResult

ROOT = Path(r"D:\AI\navoiy-tts")
PYTHON = ROOT / "venv" / "Scripts" / "python.exe"
# the owner's wish (2026-10-25): his own voice, a little emotion, a confident tone
INSTRUCT = ("Speak in a confident, warm and engaging teacher's voice with a little natural emotion, "
            "clear articulation, steady natural pacing and lively but relaxed intonation.")


def is_navoiy(voice: str) -> bool:
    return (voice or "").lower().startswith("navoiy:")


def prompt_path(voice: str) -> Path:
    return ROOT / "namuna" / f"{voice.split(':', 1)[1].strip() or 'men'}.wav"


def voice_scenes(project, scenes, progress=lambda m: None) -> list[int]:
    """Voice the given scenes with Navoiy and store the audio on them. Returns orders that failed."""
    from ..media_library import audio_duration
    from ..voice import save_scene_audio

    prompt = prompt_path(project.niche.tts_voice)
    if not PYTHON.exists() or not prompt.exists():
        raise TTSError(f"Navoiy TTS topilmadi ({PYTHON} yoki {prompt}).")
    work = ROOT / "tmp" / f"p{project.pk}"
    work.mkdir(parents=True, exist_ok=True)
    items = [{"text": s.narration.strip(), "out": str(work / f"scene_{s.order:03d}.wav")} for s in scenes]
    job = work / "job.json"
    job.write_text(json.dumps({"prompt": str(prompt), "instruct": INSTRUCT, "items": items}, ensure_ascii=False), encoding="utf-8")
    env = {**__import__("os").environ, "TMP": str(ROOT / "tmp"), "TEMP": str(ROOT / "tmp"),
           "HF_HOME": str(ROOT / "cache" / "hf"), "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.Popen([str(PYTHON), str(ROOT / "navoiy_job.py"), str(job)], cwd=ROOT, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    total = len(items)
    for line in proc.stdout:
        line = line.strip()
        if line.startswith("TODO"):
            total = int(line.split()[1].split("/")[0]) or total
        elif line.startswith("PROGRESS"):
            progress(f"Navoiy ovozi (sizning ovozingiz): {line.split()[1]} sahna (har biri ~2-4 daqiqa)...")
    proc.wait()
    failed = []
    for s, it in zip(scenes, items):
        out = Path(it["out"])
        if not out.exists():
            failed.append(s.order)
            continue
        save_scene_audio(s, TTSResult(path=out, duration=audio_duration(out)))
    return failed
