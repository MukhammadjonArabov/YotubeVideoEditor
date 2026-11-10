"""Relaxing-music videos: one short track (made once) looped into a 20-30 minute video over 1-4 looped clips.

* Music: ElevenLabs Music API (paid plan) - or any mp3 you upload. A 3-10 minute track is made once.
* Audio: the track is repeated with a soft cross-fade at every join, trimmed to the target length, faded out.
* Picture: the clips (about 20 s each, made in Google Flow) are cross-faded into one block that loops
  seamlessly (its end flows into its start), the block is repeated until the music ends.
* Subscribe + Like animations (ASS vector shapes) appear at the start and every few minutes.
"""
from __future__ import annotations

import logging
import math
import re
import subprocess
from pathlib import Path

import requests
from django.conf import settings
from django.core.files.base import ContentFile

from . import cta, media_library, render
from .subtitles import ASS_HEADER, ass_time

logger = logging.getLogger(__name__)

MUSIC_URL = "https://api.elevenlabs.io/v1/music"
DEFAULT_MUSIC_PROMPT = ("Calm, soothing nature ambience for relaxation and sleep: a soft wordless female vocalise, airy humming and gentle "
                        "\"aaah\" harmonies floating over warm pads and slow soft piano, a flowing stream, distant birdsong, light wind in "
                        "the trees. About 55 BPM, no drums, no lyrics, no spoken words, no sudden changes, the same gentle energy from "
                        "start to end, seamless and meditative.")
VOCALS_CLAUSE = "Wordless female vocals only (airy soft vocalise, humming), no lyrics, no spoken words."
INSTRUMENTAL_CLAUSE = "Instrumental only, no vocals."
FLOW_CLIP_PROMPTS = [
    "A cozy hand-drawn animated forest clearing at golden hour, a gentle stream flowing past mossy rocks, tiny birds "
    "flying between trees, leaves swaying softly, light rays slowly moving. Calm slow motion, peaceful, seamless loop, "
    "16:9, no text, no characters.",
    "A hand-drawn animated misty mountain lake at dawn, soft ripples on the water, a small wooden boat drifting slowly, "
    "mist rolling over pine hills, birds gliding far away. Very slow gentle camera drift, peaceful, 16:9, no text.",
    "A hand-drawn animated cabin in a green valley at night, warm window light, fireflies floating, stars twinkling, "
    "soft wind moving the grass, a gentle river nearby. Slow and relaxing, seamless loop, 16:9, no text.",
    "A hand-drawn animated quiet beach at sunset, small waves rolling in, palm leaves moving in a light breeze, clouds "
    "drifting across a pastel sky, seagulls far away. Calm slow motion, peaceful, 16:9, no text, no characters.",
]
XFADE_VIDEO = 1.0  # seconds of cross-fade between clips (and at the loop join)
XFADE_AUDIO_MAX = 4.0
FPS = 24
FIRST_CTA_SEC = 45
CTA_GAP = 2.0  # seconds between the Subscribe and the Like animation of one pass
END_MARGIN = 30  # no animation in the last seconds


class MusicError(RuntimeError):
    """Safe-to-show error (Uzbek)."""


# ------------------------------------------------------------------ music from ElevenLabs
def build_prompt(prompt: str, vocals: bool = True) -> str:
    """The text sent to ElevenLabs: the author's prompt plus a clear vocal / no-vocal clause."""
    text = (prompt or DEFAULT_MUSIC_PROMPT).strip()
    if vocals and "lyrics:" in text.lower():  # a sung song with its own lyrics (owner, 2026-10-31): no wordless clause
        return text[:4000]
    clause = VOCALS_CLAUSE if vocals else INSTRUMENTAL_CLAUSE
    return (text if clause.split(",")[0].lower() in text.lower() else f"{text} {clause}")[:4000]


def compose_music(prompt: str, seconds: int = 210, vocals: bool = True) -> bytes:
    """One track of `seconds` (60-300) from the ElevenLabs Music API. Needs a paid ElevenLabs plan (free plan: HTTP 402)."""
    key = (settings.ELEVENLABS_API_KEY or "").strip()
    if not key:
        raise MusicError(".env faylida ELEVENLABS_API_KEY yo'q.")
    seconds = max(60, min(300, int(seconds)))
    body = {"prompt": build_prompt(prompt, vocals), "music_length_ms": seconds * 1000,
            "force_instrumental": not vocals, "model_id": getattr(settings, "ELEVENLABS_MUSIC_MODEL", "music_v1")}
    try:
        r = requests.post(MUSIC_URL, headers={"xi-api-key": key, "Content-Type": "application/json"}, json=body, timeout=900)
    except requests.RequestException as exc:
        raise MusicError(f"ElevenLabs bilan aloqa xatosi: {exc.__class__.__name__}") from exc
    if r.status_code == 200 and len(r.content) > 10_000:
        return r.content
    detail = ""
    try:
        d = r.json().get("detail", {})
        detail = d.get("message") if isinstance(d, dict) else str(d)
    except ValueError:
        detail = r.text[:200]
    if r.status_code in (402, 403) or "paid" in (detail or "").lower():
        raise MusicError("ElevenLabs Musiqa API pullik rejani talab qiladi (bepul rejada ishlamaydi). "
                         "Rejani yangilang yoki tayyor musiqa faylini yuklang.")
    raise MusicError(f"ElevenLabs musiqa xatosi {r.status_code}: {(detail or '')[:200]}")


def add_take(mv, data: bytes, source: str = "elevenlabs", prompt: str = "", name: str = "take.mp3"):
    """Save a generated or uploaded track as a take, run the quality check, and select it when it is the first one."""
    from ..models import MusicTake
    from . import music_qc

    take = MusicTake(video=mv, source=source, prompt=prompt)
    take.file.save(name, ContentFile(data), save=False)
    take.duration = media_library.audio_duration(Path(take.file.path))
    report = music_qc.analyze(Path(take.file.path), take.duration)
    take.qc, take.score = report, report["score"]
    take.is_selected = not mv.takes.filter(is_selected=True).exists()
    take.save()
    if take.is_selected:
        select_take(mv, take)
    return take


def select_take(mv, take) -> None:
    """Use this take for the video (the others stay for comparison)."""
    mv.takes.exclude(pk=take.pk).update(is_selected=False)
    take.is_selected = True
    take.save(update_fields=["is_selected"])
    if mv.music_file:
        mv.music_file.delete(save=False)
    from django.core.files.base import ContentFile as CF

    with open(take.file.path, "rb") as fh:
        mv.music_file.save(f"music{Path(take.file.name).suffix or '.mp3'}", CF(fh.read()), save=False)
    mv.music_duration = take.duration
    mv.status = type(mv).Status.MUSIC_READY
    mv.save(update_fields=["music_file", "music_duration", "status", "updated_at"])


TRIM_SILENCE = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.3,areverse,"
                "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.3,areverse")


def trim_cmd(exe: str, track: Path, out: Path) -> list[str]:
    """Cut the silent lead-in and fade-out tail so the repeat (or the next take) follows without a gap."""
    return [exe, "-y", "-hide_banner", "-loglevel", "error", "-i", str(track), "-af", TRIM_SILENCE,
            "-c:a", "pcm_s16le", "-ar", "44100", "-ac", "2", str(out)]


def combine_cmd(exe: str, tracks: list[Path], durations: list[float], out: Path) -> list[str]:
    """Takes played one after another with soft cross-fades (1 -> 2 -> ...); the result is looped like one track."""
    xf = max(0.5, min(XFADE_AUDIO_MAX, min(durations) / 4))
    cmd = [exe, "-y", "-hide_banner", "-loglevel", "error"]
    for tr in tracks:
        cmd += ["-i", str(tr)]
    # each take is brought to the same loudness first, so the join between takes is not heard
    parts = [f"[{k}:a]{TRIM_SILENCE},loudnorm=I=-16:TP=-1.5:LRA=7[t{k}]" for k in range(len(tracks))]
    last = "[t0]"
    for k in range(1, len(tracks)):
        parts.append(f"{last}[t{k}]acrossfade=d={xf:.2f}:c1=tri:c2=tri[c{k}]")
        last = f"[c{k}]"
    parts.append(f"{last}aformat=sample_fmts=fltp:channel_layouts=stereo[out]")
    return cmd + ["-filter_complex", ";".join(parts), "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "192k", str(out)]


def combine_takes(mv, takes) -> "MusicTake":
    """All chosen takes in order as one new take (source "mix"), selected for the video."""
    takes = [t for t in takes if t.source != "mix"]
    if len(takes) < 2:
        raise MusicError("Birlashtirish uchun kamida 2 ta variant kerak.")
    out = Path(settings.MEDIA_ROOT) / "music" / f"m{mv.pk}" / "work" / "combined.mp3"
    out.parent.mkdir(parents=True, exist_ok=True)
    _run(combine_cmd(render.ffmpeg_exe(), [Path(t.file.path) for t in takes], [t.duration for t in takes], out))
    take = add_take(mv, out.read_bytes(), source="mix", name="combined.mp3")
    select_take(mv, take)
    return take


def loop_plan(music_sec: float, target_sec: float) -> dict:
    """How the track is repeated: number of passes and the cross-fade length (same maths as audio_loop_cmd)."""
    xf = max(0.5, min(XFADE_AUDIO_MAX, music_sec / 4))
    step = max(1.0, music_sec - xf)
    passes = max(1, math.ceil((target_sec - music_sec) / step) + 1) if music_sec else 0
    return {"passes": passes, "crossfade": round(xf, 1), "target_min": round(target_sec / 60, 1)}


def save_music(mv, data: bytes, name: str = "music.mp3") -> None:
    """Uploaded ready-made music: stored as a take (checked and selected when first)."""
    add_take(mv, data, source="upload", name=name)


# ------------------------------------------------------------------ plan: when the animations appear
def plan_ctas(total_sec: float, every_min: int, subscribe: bool = True, like: bool = True) -> list[tuple[float, str]]:
    """[(time in seconds, "subscribe" | "like")]: a pair at FIRST_CTA_SEC, then every `every_min` minutes."""
    if not (subscribe or like) or total_sec < FIRST_CTA_SEC + 20:
        return []
    out: list[tuple[float, str]] = []
    t = float(FIRST_CTA_SEC)
    step = max(1, int(every_min)) * 60.0
    while t < total_sec - END_MARGIN:
        if subscribe:
            out.append((round(t, 2), "subscribe"))
        if like:
            out.append((round(t + (CTA_GAP if subscribe else 0), 2), "like"))
        t += step
    return out


like_events = cta.like_events  # the LIKE button animation lives in cta.py (also used by the main render)


MOOD_FIRST = 4.0  # the title appears while the picture is still coming out of the dark
MOOD_EVERY = 720.0  # then one line from the song about every 12 minutes, between the Subscribe/Like animations
MOOD_SHOW = 9.0


def mood_times(total_sec: float, n_lines: int) -> list[float]:
    """When the soft text lines appear: the title at the start, then lines at 6:00, 18:00, 30:00 ... (none in the last minute)."""
    if n_lines <= 0:
        return []
    times = [MOOD_FIRST]
    t = 360.0
    while t + MOOD_SHOW < total_sec - END_MARGIN:
        times.append(t)
        t += MOOD_EVERY
    return times


def mood_events(lines: list[str], total_sec: float) -> list[str]:
    """Quiet text that fades in from nothing, glows softly and fades away (owner, 2026-11-09): the title first, then song lines in turn."""
    out = []
    for k, t in enumerate(mood_times(total_sec, len(lines))):
        text = (lines[0] if k == 0 else lines[1 + (k - 1) % max(1, len(lines) - 1)] if len(lines) > 1 else lines[0])
        size = 74 if k == 0 else 58
        tags = r"{\an5\pos(960,820)\fs%d\i1\b0\bord1\shad0\blur4\3c&H202020&\fad(2800,3200)}" % size
        out.append(f"Dialogue: 2,{ass_time(t)},{ass_time(t + MOOD_SHOW)},Default,,0,0,0,,{tags}{text.replace(chr(10), ' ')}\n")
    return out


def cta_ass(plan: list[tuple[float, str]], mood_lines: list[str] | None = None, total_sec: float = 0) -> str:
    out = [ASS_HEADER]
    for t, kind in plan:
        out += cta.events(t) if kind == "subscribe" else like_events(t)
    if mood_lines:
        out += mood_events(mood_lines, total_sec)
    return "".join(out)


# ------------------------------------------------------------------ ffmpeg command builders (unit-tested)
def audio_loop_cmd(exe: str, music: Path, music_sec: float, target_sec: float, out: Path) -> list[str]:
    """Repeat the track with a soft cross-fade, cut to the target length, fade out. Output: AAC."""
    xf = max(0.5, min(XFADE_AUDIO_MAX, music_sec / 4))
    step = max(1.0, music_sec - xf)
    n = max(1, min(40, math.ceil((target_sec - music_sec) / step) + 1))
    cmd = [exe, "-y", "-hide_banner", "-loglevel", "error"]
    for _ in range(n):
        cmd += ["-i", str(music)]
    parts, last = [], "[0:a]"
    for k in range(1, n):
        parts.append(f"{last}[{k}:a]acrossfade=d={xf:.2f}:c1=tri:c2=tri[a{k}]")
        last = f"[a{k}]"
    fade = min(8.0, target_sec / 4)
    parts.append(f"{last}atrim=0:{target_sec:.2f},asetpts=PTS-STARTPTS,afade=t=in:d=2,"
                 f"afade=t=out:st={max(0.0, target_sec - fade):.2f}:d={fade:.2f},loudnorm=I=-16:TP=-1.5:LRA=7,"
                 f"aformat=sample_fmts=fltp:channel_layouts=stereo[out]")
    return cmd + ["-filter_complex", ";".join(parts), "-map", "[out]", "-c:a", "aac", "-b:a", "192k", str(out)]


def loop_unit_cmd(exe: str, music: Path, music_sec: float, out: Path) -> list[str]:
    """One seamless loop of the track: its tail is cross-faded into its head, so the unit repeats without a seam.
    Two copies are cross-faded once and the part from the start of the fade to one track-length later is kept
    (a 30-pass acrossfade chain for a 3-hour video took hours; this is seconds)."""
    xf = max(0.5, min(XFADE_AUDIO_MAX, music_sec / 4))
    start, length = music_sec - xf, music_sec - xf
    return [exe, "-y", "-hide_banner", "-loglevel", "error", "-i", str(music), "-i", str(music), "-filter_complex",
            f"[0:a][1:a]acrossfade=d={xf:.2f}:c1=tri:c2=tri,atrim={start:.3f}:{start + length:.3f},asetpts=PTS-STARTPTS[out]",
            "-map", "[out]", "-c:a", "pcm_s16le", "-ar", "44100", "-ac", "2", str(out)]


def audio_from_unit_cmd(exe: str, unit: Path, target_sec: float, out: Path) -> list[str]:
    """Repeat the seamless unit to the target length, fade in and out, even loudness. Output: AAC."""
    fade = min(8.0, target_sec / 4)
    return [exe, "-y", "-hide_banner", "-loglevel", "error", "-stream_loop", "-1", "-i", str(unit), "-af",
            f"atrim=0:{target_sec:.2f},asetpts=PTS-STARTPTS,afade=t=in:d=2,afade=t=out:st={max(0.0, target_sec - fade):.2f}:d={fade:.2f},"
            f"loudnorm=I=-16:TP=-1.5:LRA=7,aformat=sample_fmts=fltp:channel_layouts=stereo",
            "-t", f"{target_sec:.2f}", "-c:a", "aac", "-b:a", "192k", str(out)]


# mean level of the clips' own nature sound, well under the music (music sits around -17..-19 dB mean); the owner
# (2026-10-30) heard the boosted clip sound over the music, so clips are only ever turned down, never up
NATURE_MEAN_DB = -42.0
NATURE_MAX_GAIN = 0.0


def clip_audio_mean(exe: str, clip: Path) -> float | None:
    """Mean volume (dB) of a clip's own sound, or None when it has no audio track."""
    err = subprocess.run([exe, "-hide_banner", "-i", str(clip), "-vn", "-af", "volumedetect", "-f", "null", "-"],
                         capture_output=True, text=True).stderr or ""
    m = re.search(r"mean_volume:\s*(-?\d+(?:\.\d+)?) dB", err)
    return float(m.group(1)) if (m and "Audio:" in err) else None


def nature_gain(mean_db: float | None) -> float | None:
    """Gain that brings a clip's nature sound to NATURE_MEAN_DB (quiet clips are not boosted into hiss)."""
    if mean_db is None or mean_db < -70:
        return None
    return max(-20.0, min(NATURE_MAX_GAIN, NATURE_MEAN_DB - mean_db))


def normalize_clip_cmd(exe: str, clip: Path, out: Path, gain_db: float | None = None, length: float = 0) -> list[str]:
    """1080p/24 fps video plus a stereo audio track: the clip's own nature sound at a set level, or silence."""
    vf = f"scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080,fps={FPS},setsar=1,format=yuv420p"
    cmd = [exe, "-y", "-hide_banner", "-loglevel", "error", "-i", str(clip)]
    if gain_db is None:
        cmd += ["-f", "lavfi", "-t", f"{max(1.0, length):.2f}", "-i", "anullsrc=r=48000:cl=stereo"]
        amap, af = "1:a", []
    else:
        amap, af = "0:a", ["-af", f"volume={gain_db:.1f}dB,aformat=sample_rates=48000:channel_layouts=stereo"]
    return cmd + ["-map", "0:v", "-map", amap, "-vf", vf, *af, "-shortest", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
                  "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", str(out)]


def block_cmd(exe: str, clips: list[Path], lengths: list[float], out: Path) -> tuple[list[str], float]:
    """One block that loops seamlessly: c1 x c2 x ... x cn x c1 (cross-faded), then cut from c1's end of the first
    fade to the end of the last one, so the block's last frame flows into its first. Returns (command, block length)."""
    d = min(XFADE_VIDEO, min(lengths) / 3)
    seq = list(clips) + [clips[0]]
    lens = list(lengths) + [lengths[0]]
    cmd = [exe, "-y", "-hide_banner", "-loglevel", "error"]
    for c in seq:
        cmd += ["-i", str(c)]
    parts, last, alast, acc = [], "[0:v]", "[0:a]", lens[0]
    for k in range(1, len(seq)):
        parts.append(f"{last}[{k}:v]xfade=transition=fade:duration={d:.2f}:offset={acc - d:.3f}[x{k}]")
        parts.append(f"{alast}[{k}:a]acrossfade=d={d:.2f}:c1=tri:c2=tri[y{k}]")  # the sound follows its picture
        last, alast, acc = f"[x{k}]", f"[y{k}]", acc + lens[k] - d
    end = acc - lens[-1] + d  # the moment the last cross-fade is complete
    length = end - d
    parts.append(f"{last}trim=start={d:.3f}:end={end:.3f},setpts=PTS-STARTPTS,format=yuv420p[v]")
    parts.append(f"{alast}atrim=start={d:.3f}:end={end:.3f},asetpts=PTS-STARTPTS[a]")
    cmd += ["-filter_complex", ";".join(parts), "-map", "[v]", "-map", "[a]", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast",
            "-crf", "22", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", str(out)]
    return cmd, length


def final_cmd(exe: str, block: Path, audio: Path, ass_name: str, target_sec: float, out: Path) -> list[str]:
    """Loop the block over the whole track, burn in the animations, mux with the looped audio (cwd = the folder with the .ass)."""
    return [exe, "-y", "-hide_banner", "-loglevel", "error", "-progress", "pipe:1", "-nostats", "-stream_loop", "-1", "-i", str(block),
            "-i", str(audio), "-filter_complex",
            f"[0:v]fade=t=in:st=0:d=4,fade=t=out:st={max(0.0, target_sec - 4):.2f}:d=4,ass={ass_name}[v];[1:a][0:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.8[a]",
            "-map", "[v]", "-map", "[a]", "-t", f"{target_sec:.2f}",
            "-c:v", "libx264", "-preset", "superfast", "-crf", "27", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)]


# ------------------------------------------------------------------ orchestration
def _run(cmd: list[str], cwd: Path | None = None, timeout: int = 7200) -> None:
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise MusicError(f"ffmpeg xatosi: {(r.stderr or '')[-400:]}")


def _run_with_progress(cmd: list[str], cwd: Path, total_sec: float, progress, timeout: int = 14400) -> None:
    proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    last = -1
    try:
        for line in proc.stdout:  # "out_time_us=123456"
            m = re.match(r"out_time_(?:us|ms)=(\d+)", line.strip())
            if m:
                pct = min(99, int(int(m.group(1)) / 1_000_000 / max(1.0, total_sec) * 100))
                if pct != last and pct % 2 == 0:
                    last = pct
                    progress(f"Montaj: {pct}% ({total_sec / 60:.0f} daqiqalik video kodlanmoqda)")
        proc.wait(timeout=timeout)
    except Exception:
        proc.kill()
        raise
    if proc.returncode != 0:
        raise MusicError(f"ffmpeg xatosi: {(proc.stderr.read() or '')[-400:]}")


def render_music_video(mv, progress=lambda m: None, target_sec: float | None = None) -> tuple[Path, float]:
    """Everything in order. Needs a music file and 1-4 clips. Returns (mp4 path, seconds)."""
    exe = render.ffmpeg_exe()
    clips = list(mv.clips.order_by("order"))
    if not mv.music_file:
        raise MusicError("Avval musiqa yarating yoki yuklang.")
    if not clips:
        raise MusicError("Kamida bitta video klip yuklang.")
    music = Path(mv.music_file.path)
    music_sec = mv.music_duration or media_library.audio_duration(music)
    if music_sec < 8:
        raise MusicError("Musiqa juda qisqa (kamida 8 soniya).")
    total = float(target_sec or mv.target_minutes * 60)
    work = Path(settings.MEDIA_ROOT) / "music" / f"m{mv.pk}" / "work"
    work.mkdir(parents=True, exist_ok=True)

    progress("Musiqa takrorlanmoqda (yumshoq ulanish bilan)...")
    trimmed = work / "music_trim.wav"
    _run(trim_cmd(exe, music, trimmed))
    if media_library.audio_duration(trimmed) >= 8:
        music, music_sec = trimmed, media_library.audio_duration(trimmed)
    audio = work / "audio_loop.m4a"
    unit = work / "loop_unit.wav"
    _run(loop_unit_cmd(exe, music, music_sec, unit))
    _run(audio_from_unit_cmd(exe, unit, total, audio))

    progress("Klip(lar) tayyorlanmoqda...")
    normalized, lengths = [], []
    for c in clips:
        out = work / f"norm_{c.order:02d}.mp4"
        src = Path(c.file.path)
        _run(normalize_clip_cmd(exe, src, out, nature_gain(clip_audio_mean(exe, src)), c.duration or media_library.audio_duration(src)))
        normalized.append(out)
        lengths.append(media_library.audio_duration(out) or c.duration or 20.0)
    progress("Klip bloki (uzluksiz takrorlanadigan) yig'ilmoqda...")
    block = work / "block.mp4"
    cmd, block_len = block_cmd(exe, normalized, lengths, block)
    _run(cmd)

    plan = plan_ctas(total, mv.cta_every_min, mv.add_subscribe, mv.add_like)
    ass_text = cta_ass(plan, (mv.kit or {}).get("mood_lines") or [], total)
    (work / "cta.ass").write_text(ass_text, encoding="utf-8")
    final = work / "final.mp4"
    progress(f"Montaj boshlandi: {total / 60:.0f} daqiqa, {len(plan)} ta animatsiya...")
    try:
        fast_final(exe, block, block_len, audio, ass_text, total, work, final, progress)
    except Exception:  # noqa: BLE001  the copy-based path is an optimisation; the full encode always works
        logger.exception("Fast music montage failed, falling back to the full encode")
        _run_with_progress(final_cmd(exe, block, audio, "cta.ass", total, final), work, total, progress)
    return final, total


# ------------------------------------------------------------------ fast final montage (owner, 2026-11-09)
# A music video is one short block repeated for hours. Encoding every frame of 3 hours took 1.5-3 h on the owner's
# i3 laptop. Instead the block is encoded once with a keyframe every second and a whole-second length, repeated by
# stream copy, and only the seconds with text, animations or the fades are encoded again; everything is joined by copy.
_ENCODER: list[str] | None = None


def video_encoder(exe: str) -> list[str]:
    """Intel Quick Sync when the machine has it (about 2x faster on the owner's laptop), else x264. Checked once."""
    global _ENCODER
    if _ENCODER is None:
        probe = subprocess.run([exe, "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc=size=640x360:rate=24",
                                "-t", "1", "-c:v", "h264_qsv", "-f", "null", "-"], capture_output=True, timeout=60)
        _ENCODER = (["-c:v", "h264_qsv", "-global_quality", "29", "-look_ahead", "0", "-idr_interval", "0", "-forced_idr", "1"] if probe.returncode == 0
                    else ["-c:v", "libx264", "-preset", "veryfast", "-crf", "23"])
    return _ENCODER + ["-pix_fmt", "nv12" if "h264_qsv" in _ENCODER else "yuv420p", "-r", str(FPS), "-g", str(FPS),
                       "-bf", "0", "-force_key_frames", "expr:gte(t,n_forced*1)"]


_DIALOGUE = re.compile(r"^(Dialogue: [^,]*,)(\d+:\d\d:\d\d\.\d\d),(\d+:\d\d:\d\d\.\d\d),(.*)$")


def _ass_sec(s: str) -> float:
    h, m, sec = s.split(":")
    return int(h) * 3600 + int(m) * 60 + float(sec)


def overlay_windows(ass_text: str, total: float, fade: float = 4.0) -> list[tuple[int, int]]:
    """Whole-second spans that need encoding: every ASS event (plus a second each side), the fade-in and the fade-out."""
    spans = [(0, int(math.ceil(fade)) + 2), (max(0, int(math.floor(total - fade)) - 1), int(math.ceil(total)))]
    for line in ass_text.splitlines():
        m = _DIALOGUE.match(line)
        if m:
            spans.append((max(0, int(math.floor(_ass_sec(m.group(2)))) - 1), min(int(math.ceil(total)), int(math.ceil(_ass_sec(m.group(3)))) + 1)))
    spans.sort()
    merged: list[list[int]] = []
    for a, b in spans:
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    return [(a, b) for a, b in merged if b > a]


def shifted_ass(ass_text: str, start: float, end: float) -> str:
    """The ASS file for one window: events that touch it, moved so the window starts at 0."""
    out = []
    for line in ass_text.splitlines():
        m = _DIALOGUE.match(line)
        if not m:
            out.append(line)
            continue
        s, e = _ass_sec(m.group(2)), _ass_sec(m.group(3))
        if e <= start or s >= end:
            continue
        out.append(f"{m.group(1)}{ass_time(s - start)},{ass_time(e - start)},{m.group(4)}")
    return "\n".join(out) + "\n"


def fast_final(exe: str, block: Path, block_len: float, music_audio: Path, ass_text: str, total: float, work: Path,
               out: Path, progress=lambda m: None) -> None:
    enc = video_encoder(exe)
    unit = int(math.ceil(block_len))
    factor = unit / block_len
    # 1. the block, stretched by under a second to a whole-second length, keyframe every second; its own sound separately
    bv, ba = work / "block_v.mp4", work / "block_a.wav"
    _run([exe, "-y", "-hide_banner", "-loglevel", "error", "-i", str(block), "-vf", f"setpts=PTS*{factor:.6f},fps={FPS},format=yuv420p",
          "-t", str(unit), "-an", *enc, str(bv)])
    _run([exe, "-y", "-hide_banner", "-loglevel", "error", "-i", str(block), "-vn", "-af", f"atempo={1 / factor:.6f}",
          "-t", str(unit), "-c:a", "pcm_s16le", "-ar", "44100", "-ac", "2", str(ba)])
    # 2. the block cut by copy into one-second pieces (exact: a keyframe starts every second); second s of the video
    #    is piece s % unit, so the whole timeline is a list of pieces and nothing is cut inexactly
    for old in work.glob("sec_*.mp4"):
        old.unlink()
    _run([exe, "-y", "-hide_banner", "-loglevel", "error", "-i", bv.name, "-c", "copy", "-f", "segment", "-segment_time", "1",
          "-reset_timestamps", "1", "sec_%04d.mp4"], cwd=work)
    pieces = sorted(work.glob("sec_*.mp4"))
    if len(pieces) != unit:
        raise MusicError(f"blok {unit} soniya, bo'laklar {len(pieces)} ta")

    def piece(s: int) -> str:
        return f"file '{pieces[s % unit].name}'\n"

    # 3. only the seconds with text / animation / fades are encoded again
    windows = overlay_windows(ass_text, total)
    seconds = int(math.ceil(total))
    parts, t = [], 0
    for k, (a, b) in enumerate(windows):
        parts += [piece(s) for s in range(t, a)]
        src = work / f"win_{k:03d}_in.txt"
        src.write_text("".join(piece(s) for s in range(a, b)), encoding="utf-8")
        ass_name = f"win_{k:03d}.ass"
        (work / ass_name).write_text(shifted_ass(ass_text, a, b), encoding="utf-8")
        vf = []
        if a == 0:
            vf.append("fade=t=in:st=0:d=4")
        if b >= total - 0.01:
            vf.append(f"fade=t=out:st={max(0.0, total - 4 - a):.2f}:d=4")
        vf.append(f"ass={ass_name}")
        win = work / f"win_{k:03d}.mp4"
        _run([exe, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", src.name,
              "-vf", ",".join(vf), "-an", *enc, win.name], cwd=work)
        parts.append(f"file '{win.name}'\n")
        t = b
        if k % 5 == 0:
            progress(f"Montaj: {int(100 * b / total)}% (faqat matn/animatsiyali joylar kodlanmoqda, qolgani nusxalanadi)")
    parts += [piece(s) for s in range(t, seconds)]
    plst = work / "parts.txt"
    plst.write_text("".join(parts), encoding="utf-8")
    video = work / "video_full.mp4"
    _run([exe, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", plst.name, "-c", "copy", video.name], cwd=work)
    # 4. sound: the music plus the clips' own (quiet) sound, looped under it
    progress("Montaj: ovoz yig'ilmoqda...")
    _run([exe, "-y", "-hide_banner", "-loglevel", "error", "-i", str(music_audio), "-stream_loop", "-1", "-i", str(ba),
          "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.8[a]", "-map", "[a]",
          "-t", f"{total:.2f}", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(work / "audio_full.m4a")])
    _run([exe, "-y", "-hide_banner", "-loglevel", "error", "-i", str(video), "-i", str(work / "audio_full.m4a"), "-map", "0:v", "-map", "1:a",
          "-c", "copy", "-t", f"{total:.2f}", "-movflags", "+faststart", str(out)])
