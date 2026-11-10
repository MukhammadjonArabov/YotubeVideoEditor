"""Automatic quality check of a relaxing-music track (so a bad take is caught before a 30-minute video is made).

Checks (Uzbek messages, see niches/Musiqa.md section 4): loudness, true peak, loudness range, silence gaps in the middle, how
well the end matches the start (the track is looped), length, and sudden loudness jumps. The score is 0-100; below 70 or any
"bad" issue means: make another take. Whether the female voice sounds natural is still judged by ear (the site player).
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from . import media_library, render

TARGET_LUFS = (-23.0, -14.0)
MAX_PEAK_DB = -1.0
MAX_LRA = 6.0
MAX_SEAM_DB = 3.0
MAX_JUMP_DB = 6.0
SILENCE_GAP = 1.5  # seconds of silence in the middle that count as a break
EDGE = 3.0  # silence this close to the start/end is a normal fade
LENGTH_OK = (150.0, 300.0)
SAMPLE_RATE = 16000


def _ffmpeg(args: list[str], timeout: int = 600) -> str:
    """Run ffmpeg and return stderr (the analysis filters print there)."""
    proc = subprocess.run([render.ffmpeg_exe(), "-hide_banner", "-nostats", *args], capture_output=True, text=True, timeout=timeout)
    return proc.stderr or ""


def loudness(path: Path) -> dict:
    """Integrated loudness (LUFS), loudness range (LU) and true peak (dBFS) from ffmpeg's ebur128 summary."""
    err = _ffmpeg(["-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"])
    tail = err[err.rfind("Summary:"):] if "Summary:" in err else err
    out: dict = {}
    for key, pattern in (("lufs", r"I:\s+(-?\d+(?:\.\d+)?)\s+LUFS"), ("lra", r"LRA:\s+(-?\d+(?:\.\d+)?)\s+LU"),
                         ("peak_db", r"Peak:\s+(-?\d+(?:\.\d+)?)\s+dBFS")):
        m = re.search(pattern, tail)
        out[key] = float(m.group(1)) if m else None
    return out


def silences(path: Path, total: float) -> list[tuple[float, float]]:
    """Silent stretches (start, end) of at least SILENCE_GAP seconds that are not just the fade at the very start/end."""
    err = _ffmpeg(["-i", str(path), "-af", f"silencedetect=noise=-50dB:d={SILENCE_GAP}", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start:\s*(-?\d+(?:\.\d+)?)", err)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*(-?\d+(?:\.\d+)?)", err)]
    out = []
    for i, s in enumerate(starts):
        e = ends[i] if i < len(ends) else total
        if s > EDGE and e < total - EDGE:
            out.append((round(s, 1), round(e, 1)))
    return out


def decode_mono(path: Path):
    import numpy as np

    proc = subprocess.run([render.ffmpeg_exe(), "-v", "error", "-i", str(path), "-f", "s16le", "-ac", "1", "-ar", str(SAMPLE_RATE), "-"],
                          capture_output=True, timeout=600)
    return np.frombuffer(proc.stdout, dtype=np.int16).astype("float32") / 32768.0


def window_levels(samples, window_sec: float = 2.0):
    """RMS level in dB of consecutive windows."""
    import numpy as np

    n = int(window_sec * SAMPLE_RATE)
    if len(samples) < n * 2:
        return np.array([])
    count = len(samples) // n
    frames = samples[: count * n].reshape(count, n)
    rms = np.sqrt((frames ** 2).mean(axis=1) + 1e-12)
    return 20 * np.log10(rms + 1e-9)


def edge_gap_db(levels, edge_windows: int = 4) -> float | None:
    """Level difference between the first and the last few windows (loop join): small = the repeat is hard to notice."""
    if len(levels) < edge_windows * 3:
        return None
    return float(abs(levels[:edge_windows].mean() - levels[-edge_windows:].mean()))


def biggest_jump_db(levels, skip: int = 2) -> float:
    """Largest loudness step between neighbouring windows in the middle of the track."""
    mid = levels[skip:-skip] if len(levels) > skip * 2 + 2 else levels
    if len(mid) < 2:
        return 0.0
    return float(abs(mid[1:] - mid[:-1]).max())


def analyze(path: Path, duration: float | None = None) -> dict:
    """{score, metrics, issues:[{level: "bad"|"warn", text}]} for one track."""
    path = Path(path)
    total = duration or media_library.audio_duration(path)
    metrics: dict = {"duration": round(total, 1)}
    issues: list[dict] = []
    score = 100.0

    def issue(level: str, text: str, penalty: float) -> None:
        nonlocal score
        issues.append({"level": level, "text": text})
        score -= penalty

    if not (LENGTH_OK[0] <= total <= LENGTH_OK[1]):
        issue("warn", f"Uzunligi {total:.0f} soniya: 150-300 soniya (3-5 daqiqa) bo'lgani yaxshi.", 8)

    ld = loudness(path)
    metrics.update(ld)
    lufs, lra, peak = ld.get("lufs"), ld.get("lra"), ld.get("peak_db")
    if lufs is None:
        issue("bad", "Balandlikni o'lchab bo'lmadi (fayl buzuq bo'lishi mumkin).", 40)
    else:
        if lufs < TARGET_LUFS[0]:
            issue("warn", f"Ovoz juda past ({lufs:.1f} LUFS). Montajda balandlik tekislanadi, lekin yaxshisi ~-16 LUFS.", 8)
        elif lufs > TARGET_LUFS[1]:
            issue("bad", f"Ovoz juda baland ({lufs:.1f} LUFS): tinchlantiruvchi musiqa uchun mos emas.", 20)
    if peak is not None and peak > MAX_PEAK_DB:
        issue("bad", f"Cho'qqi {peak:.1f} dBFS: tovush qirqilishi (buzilish) bo'lishi mumkin.", 18)
    if lra is not None and lra > MAX_LRA:
        issue("warn", f"Balandlik o'zgarishi katta (LRA {lra:.1f} LU): uyqu musiqasi bir tekis bo'lishi kerak.", min(20.0, (lra - MAX_LRA) * 3))

    gaps = silences(path, total)
    metrics["silences"] = gaps
    if gaps:
        issue("bad", f"Trek o'rtasida jimlik bor: {', '.join(f'{a:.0f}-{b:.0f} s' for a, b in gaps[:3])}. Musiqa uzilib qolgan.", min(30.0, 15.0 * len(gaps)))

    try:
        levels = window_levels(decode_mono(path))
    except Exception:  # noqa: BLE001 - numpy/ffmpeg trouble must not break the check
        levels = []
    if len(levels):
        seam = edge_gap_db(levels)
        jump = biggest_jump_db(levels)
        metrics["seam_db"] = None if seam is None else round(seam, 1)
        metrics["max_jump_db"] = round(jump, 1)
        if seam is not None and seam > MAX_SEAM_DB:
            issue("warn", f"Boshi va oxiri balandligi {seam:.1f} dB farq qiladi: takrorlash ulanishi sezilishi mumkin.", min(20.0, (seam - MAX_SEAM_DB) * 4))
        if jump > MAX_JUMP_DB:
            issue("warn", f"Treknda keskin balandlik sakrashi bor ({jump:.1f} dB): bir tekis emas.", 10)

    score = max(0, min(100, round(score)))
    if score >= 85 and not issues:
        verdict = "A'lo: montajga tayyor."
    elif score >= 70 and not any(i["level"] == "bad" for i in issues):
        verdict = "Yaxshi: ishlatsa bo'ladi, ogohlantirishlarni ko'ring."
    else:
        verdict = "Qoniqarsiz: boshqa take yarating."
    return {"score": score, "verdict": verdict, "metrics": metrics, "issues": issues}


def loop_preview_cmd(exe: str, music: Path, music_sec: float, out: Path, seconds: float = 20.0) -> list[str]:
    """A short clip of the repeat point: the end of the track cross-faded into its start, to listen to the join."""
    xf = max(0.5, min(4.0, music_sec / 4))
    half = seconds / 2
    return [exe, "-y", "-hide_banner", "-loglevel", "error", "-i", str(music), "-i", str(music), "-filter_complex",
            f"[0:a]atrim={max(0.0, music_sec - half - xf):.2f}:{music_sec:.2f},asetpts=PTS-STARTPTS[a];"
            f"[1:a]atrim=0:{half + xf:.2f},asetpts=PTS-STARTPTS[b];[a][b]acrossfade=d={xf:.2f}:c1=tri:c2=tri[o]",
            "-map", "[o]", "-c:a", "libmp3lame", "-b:a", "160k", str(out)]
