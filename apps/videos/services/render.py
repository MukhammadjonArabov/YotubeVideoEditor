"""ffmpeg rendering, v2 (phases 4 + 7).

Per scene: still image -> eased Ken Burns (zoompan) + processed narration (+0.4 s pad)
+ SFX + burned-in ASS captions -> cached clip. A scene's clip opens with an xfade transition
out of the previous scene's final frame, so clips can still be joined with the concat demuxer
(video stream copy, no re-encode, nothing held in memory). Clip audio is kept as PCM so it is
encoded to AAC only once, in the final mix, where music is ducked under the voice and the whole
track is normalized to YouTube loudness (-14 LUFS).

Scene clips are rendered in parallel (RENDER_WORKERS ffmpeg processes).
"""
from __future__ import annotations

import hashlib
import logging
import math
import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)

FPS = 30
PAD = 0.4  # seconds of silence after each scene's narration
HOOK_PAD = 0.12  # hook lines follow each other tightly (one sentence per scene, fast pictures)
RENDER_VERSION = "v5"
MOTIONS = ["zoom_in", "pan_right", "zoom_out", "pan_left", "diagonal"]
QUALITIES = {
    "preview": {"size": (1280, 720), "prescale": 1.5, "x264": ["-preset", "ultrafast", "-crf", "26"], "qsv": ["-preset", "veryfast", "-global_quality", "27"]},
    "final": {"size": (1920, 1080), "prescale": 1.5, "x264": ["-preset", "veryfast", "-crf", "20", "-profile:v", "high"], "qsv": ["-preset", "medium", "-global_quality", "21"]},
}

# ---- transitions & sound design
TRANSITION_SEC = 0.5
FADE_IN_SEC = 0.15  # the video starts almost instantly - no slow fade eating the hook
FADE_OUT_SEC = 1.0  # last scene goes down to black
# Scene.Transition names -> ffmpeg xfade names (older xfade names pass through unchanged).
XFADE_NAMES = {"crossfade": "fade", "whip": "smoothleft", "dip_to_black": "fadeblack", "flash": "fadewhite"}
# Durations per xfade name (default TRANSITION_SEC); "whip" uses WHIP_SEC.
TRANSITION_SECONDS = {"fade": 0.4, "fadewhite": 0.2, "fadeblack": 0.6}
WHIP_SEC = 0.25
FLASH_TRANSITIONS = {"fadewhite", "fadeblack"}
# Automatic rotation: mostly calm dissolves and smooth pushes, with hard cuts for rhythm.
AUTO_TRANSITIONS = ["fade", "smoothleft", "cut", "fade", "smoothright", "zoomin", "cut", "circleopen"]
# Movement-type transitions get a quiet whoosh; dissolves stay silent.
WHOOSH_TRANSITIONS = {"smoothleft", "smoothright", "slideleft", "slideright", "slideup", "slidedown", "wipeleft",
                      "wiperight", "zoomin", "circleopen", "circleclose", "pixelize", "radial"}
TRANSITION_SFX_VOLUME = 0.35
FLASH_SFX_VOLUME = 0.6
CUE_SFX_VOLUME = 0.4  # ~ -8 dB, used when a hit has no explicit gain
# Narration polish: cut rumble, even out the level so words don't get lost under music.
# Softer, warmer narration: cut rumble, a touch of low-mid warmth, tame the harsh 3 kHz edge and the
# "s" sounds, then even out the level so words don't get lost under the music.
VOICE_FX = ("highpass=f=70,equalizer=f=180:t=q:w=1:g=1.5,equalizer=f=3200:t=q:w=1.4:g=-2.5,deesser=i=0.4,"
            "acompressor=threshold=0.1:ratio=2.5:attack=8:release=180:makeup=1.5")
LIMITER = "alimiter=limit=0.95:level=0"
LOUDNESS_LUFS = -14.0
MUSIC_DB = -15.0  # music level before ducking; it drops ~8-10 dB more while someone speaks

# ---- camera & shots
# director's camera_move -> zoompan motion ("" = automatic rotation)
CAMERA_MOTIONS = {"none": "still", "slow_zoom_in": "zoom_in", "slow_zoom_out": "zoom_out", "pan_left": "pan_left",
                  "pan_right": "pan_right", "punch_zoom": "punch", "shake": "shake"}
# A scene is cut into several framings of its picture (jump cuts at word starts): in the hook the view
# changes every ~1.6 s, later every ~4 s.
HOOK_SHOT_SEC, BODY_SHOT_SEC = 2.0, 3.5  # a new framing / cut about every 2 s in the hook, 3-4 s after it
HOOK_MIN_SHOT_SEC, BODY_MIN_SHOT_SEC = 0.9, 1.8
JUMP_FRAMINGS = ["jump", "jump_l", "jump_r"]
PUNCH_FRAMES = 8  # ~0.27 s push-in
SHAKE_FRAMES = 10  # ~0.33 s shake that dies out
VIGNETTE = "vignette=angle=PI/7"  # very light; corners only
# ---- hook sound design
HOOK_IMPACT_DB = -12.0  # soft hit when the music drops in after the first line
HOOK_RISER_DB = -14.0  # riser into the main part
DROP_OUT_LEVEL, SWELL_LEVEL, MOOD_DIP_LEVEL = 0.12, 1.7, 0.4


class RenderError(RuntimeError):
    """Carries the failing command + stderr for Project.error_message."""


# ------------------------------------------------------------------ ffmpeg discovery
@lru_cache(maxsize=1)
def ffmpeg_exe() -> str:
    """FFMPEG_PATH if it exists (file or on PATH), otherwise the ffmpeg bundled with imageio-ffmpeg."""
    configured = (settings.FFMPEG_PATH or "ffmpeg").strip().strip('"')
    if Path(configured).is_file():
        return configured
    found = shutil.which(configured)
    if found:
        return found
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:  # noqa: BLE001
        raise RenderError("ffmpeg topilmadi. `pip install imageio-ffmpeg` qiling yoki .env da FFMPEG_PATH ni ko'rsating.") from exc


def _run(cmd: list[str], cwd: Path | None = None, timeout: int = 3600) -> None:
    proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)
    if proc.returncode != 0:
        raise RenderError(f"ffmpeg xatosi (kod {proc.returncode}).\n\nBUYRUQ:\n{' '.join(cmd)}\n\nSTDERR:\n{proc.stderr[-3000:]}")


@lru_cache(maxsize=1)
def capabilities() -> dict:
    exe = ffmpeg_exe()
    enc = subprocess.run([exe, "-hide_banner", "-encoders"], capture_output=True, text=True, errors="replace").stdout
    flt = subprocess.run([exe, "-hide_banner", "-filters"], capture_output=True, text=True, errors="replace").stdout
    qsv = False
    if " h264_qsv " in enc:  # listed != usable: try a 1-frame encode on this machine
        test = subprocess.run([exe, "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=black:s=320x240:d=0.1",
                               "-frames:v", "1", "-c:v", "h264_qsv", "-f", "null", "-"], capture_output=True, text=True)
        qsv = test.returncode == 0
    return {"qsv": qsv, "ass": " ass " in flt, "xfade": " xfade " in flt, "duck": " sidechaincompress " in flt,
            "loudnorm": " loudnorm " in flt, "exe": exe}


def video_codec_args(quality: str, caps: dict | None = None) -> list[str]:
    caps = caps if caps is not None else capabilities()
    q = QUALITIES[quality]
    if caps.get("qsv"):
        return ["-c:v", "h264_qsv", *q["qsv"]]
    return ["-c:v", "libx264", *q["x264"], "-pix_fmt", "yuv420p"]


def render_workers() -> int:
    """Parallel ffmpeg processes: RENDER_WORKERS from .env, else half the CPU threads (2 on an i3)."""
    configured = int(getattr(settings, "RENDER_WORKERS", 0) or 0)
    if configured > 0:
        return configured
    return max(1, min(4, (os.cpu_count() or 2) // 2))


# ------------------------------------------------------------------ command builders (unit-tested)
def motion_for(index: int) -> str:
    return MOTIONS[index % len(MOTIONS)]


def frame_count(duration: float) -> int:
    return max(1, math.ceil(duration * FPS))


def zoompan_expr(motion: str, frames: int, hook: bool = False, offset: int = 0) -> tuple[str, str, str]:
    """(z, x, y) expressions for ffmpeg zoompan. `on` = output frame number.

    Movement is eased (slow start, slow stop) instead of linear, which reads as a camera move
    rather than a slideshow. Progress is clamped at 1, so `offset` >= frames-1 gives the frozen
    final frame (used to start the next scene's transition exactly where this one ended).
    """
    n = max(1, frames - 1)
    p = f"min((on+{offset})/{n},1)" if offset else f"on/{n}"
    ease = f"(0.5-0.5*cos(PI*{p}))"  # ease-in-out
    center_x, center_y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    if hook:  # faster, stronger push-in for the opening scenes (ease-out: punchy start)
        return f"1+0.22*(1-pow(1-{p},2))", center_x, center_y
    if motion == "still":  # "no movement" still breathes a little, so the picture never looks frozen
        return f"1.02+0.02*{ease}", center_x, center_y
    if motion == "punch":  # quick push-in, then a slow drift
        q = f"min((on+{offset})/{PUNCH_FRAMES},1)"
        return f"1+0.14*(1-pow(1-{q},3))+0.03*{ease}", center_x, "(ih-ih/zoom)*0.45"
    if motion == "shake":  # a short, dying shake for a scary hit
        d = f"max(0,1-(on+{offset})/{SHAKE_FRAMES})"
        return (f"1.06+0.03*{ease}", f"{center_x}+14*sin((on+{offset})*2.3)*{d}",
                f"{center_y}+10*cos((on+{offset})*2.9)*{d}")
    if motion == "jump":  # later shot of a scene: cut in closer, upper-middle (faces)
        return f"1.22+0.05*{ease}", "(iw-iw/zoom)*0.5", "(ih-ih/zoom)*0.4"
    if motion in ("jump_l", "jump_r"):  # closer on the left / right third
        side = "0.15" if motion == "jump_l" else "0.85"
        return f"1.26+0.04*{ease}", f"(iw-iw/zoom)*{side}", "(ih-ih/zoom)*0.42"
    if motion == "zoom_in":
        return f"1+0.12*{ease}", center_x, center_y
    if motion == "zoom_out":
        return f"1.12-0.12*{ease}", center_x, center_y
    if motion == "pan_right":
        return "1.10", f"(iw-iw/zoom)*{ease}", center_y
    if motion == "pan_left":
        return "1.10", f"(iw-iw/zoom)*(1-{ease})", center_y
    return f"1.05+0.07*{ease}", f"(iw-iw/zoom)*0.6*{ease}", f"(ih-ih/zoom)*0.6*{ease}"  # diagonal


def motion_for_scene(index: int, scene, prev_motion: str = "") -> str:
    """The director's camera move, else the automatic rotation (never the same move twice in a row).
    The first scene of the video opens with a punch-in."""
    chosen = CAMERA_MOTIONS.get((getattr(scene, "camera_move", "") or "").strip())
    if chosen:
        return chosen
    if index == 0:
        return "punch"
    motion = motion_for(index)
    return motion_for(index + 1) if motion == prev_motion else motion


def split_points(duration: float, voice_len: float, words: list[dict] | None, hook: bool) -> list[float]:
    """Cut times inside a scene for its extra framings: every ~HOOK_SHOT_SEC in the hook, ~BODY_SHOT_SEC
    later, each snapped to the nearest word start so a cut never lands mid-word. [] = one shot."""
    target, min_shot = (HOOK_SHOT_SEC, HOOK_MIN_SHOT_SEC) if hook else (BODY_SHOT_SEC, BODY_MIN_SHOT_SEC)
    n = round(duration / target)
    if n < 2:
        return []
    starts = sorted(w["start"] for w in (words or []) if "start" in w)
    span = voice_len if voice_len > min_shot * n else duration
    cuts, last = [], 0.0
    for k in range(1, n):
        ideal = span * k / n
        options = [t for t in starts if t - last >= min_shot and duration - t >= min_shot] or \
                  ([ideal] if ideal - last >= min_shot and duration - ideal >= min_shot else [])
        if not options:
            break
        t = round(min(options, key=lambda x: abs(x - ideal)), 3)
        if abs(t - ideal) > target * 0.6:  # no word start nearby: cut on time instead
            t = round(ideal, 3)
            if t - last < min_shot or duration - t < min_shot:
                continue
        cuts.append(t)
        last = t
    return cuts


def shot_list(motion: str, duration: float, cuts: list[float]) -> list[tuple[str, int]]:
    """[(motion, frames)] for a scene cut at `cuts`: the scene's own move first, then rotating close framings."""
    if not cuts:
        return []
    edges = [0.0, *cuts, duration]
    frames = [frame_count(edges[k + 1]) - frame_count(edges[k]) if k else frame_count(edges[1])
              for k in range(len(edges) - 1)]
    frames[-1] = frame_count(duration) - sum(frames[:-1])
    motions = [motion] + [JUMP_FRAMINGS[k % len(JUMP_FRAMINGS)] for k in range(len(frames) - 1)]
    return list(zip(motions, frames))


def music_gain_expr(windows: list[tuple[float, float, float, float]]) -> str | None:
    """ffmpeg volume expression for music cues: windows of (start, end, level, ramp seconds)."""
    terms = [f"(1+({lvl}-1)*clip((t-{a:.2f})/{r},0,1)*clip(({b:.2f}-t)/{r},0,1))" for a, b, lvl, r in windows]
    return "*".join(terms) or None


def transition_duration(transition: str, whip: bool = False) -> float:
    return WHIP_SEC if whip else TRANSITION_SECONDS.get(transition, TRANSITION_SEC)


def plan_transition(index: int, scene, used_jarring: set[str] | None = None) -> str:
    """xfade name into this scene, or "" for a hard cut. The scene's own choice wins, else automatic:
    hook scenes stay hard cuts (pace), punchlines get a white flash, the rest rotate."""
    if index == 0:
        return ""
    chosen = (getattr(scene, "transition_in", "") or "").strip()
    if chosen:
        if chosen == "cut":
            return ""
        if used_jarring is not None and chosen in settings.JARRING_TRANSITIONS:
            if chosen in used_jarring:
                return "fade"
            used_jarring.add(chosen)
        return XFADE_NAMES.get(chosen, chosen)
    if scene.beat_type == "hook":
        return ""
    if scene.beat_type == "punchline":
        return "fadewhite"
    auto = AUTO_TRANSITIONS[index % len(AUTO_TRANSITIONS)]
    return "" if auto == "cut" else auto


def transition_sfx_tag(transition: str, scene_tags=()) -> str | None:
    """Sound under a transition; skipped when the scene already has its own sound of that kind."""
    if isinstance(scene_tags, str):
        scene_tags = [scene_tags] if scene_tags else []
    tags = set(scene_tags)
    if not transition or transition == "fadeblack":
        return None
    if transition == "fadewhite":
        return None if tags else "impact"
    if transition in WHOOSH_TRANSITIONS and not tags & {"whoosh", "swoosh"}:
        return "whoosh"
    return None


def db_to_gain(db: float) -> float:
    return round(10 ** (float(db) / 20), 3)


def scene_sfx_items(scene) -> list[dict]:
    """The scene's SFX list, cleaned: known tags only, sorted by time."""
    out = []
    for item in getattr(scene, "sfx", None) or []:
        if not isinstance(item, dict):
            continue
        tag = str(item.get("tag", "")).strip().lower()
        if tag not in settings.SFX_TAGS:
            continue
        try:
            offset = max(0, int(item.get("offset_ms", 0) or 0))
            gain = max(-40.0, min(6.0, float(item.get("gain_db", settings.SFX_GAIN_DB))))
        except (TypeError, ValueError):
            continue
        out.append({"tag": tag, "offset_ms": offset, "gain_db": gain})
    return sorted(out, key=lambda x: x["offset_ms"])


@dataclass
class SfxHit:
    path: Path
    volume: float = CUE_SFX_VOLUME
    delay: float = 0.0  # seconds from the start of the clip


@dataclass
class ClipSpec:
    image: Path
    audio: Path
    out: Path
    duration: float
    motion: str
    size: tuple[int, int]
    prescale: float
    codec_args: list[str]
    hook: bool = False
    sfx: list[SfxHit] = field(default_factory=list)
    subtitles: str | None = None  # file name relative to the working dir (ffmpeg runs with cwd there)
    # transition in from the previous scene (its image is re-drawn at its final Ken Burns position)
    transition: str = ""
    transition_sec: float = 0.0  # 0 = default for this xfade
    prev_image: Path | None = None
    prev_motion: str = ""
    prev_frames: int = 0
    prev_hook: bool = False
    fade_in: bool = False
    fade_out: bool = False
    threads: int = 0
    shots: list[tuple[str, int]] = field(default_factory=list)  # [(motion, frames)]; empty = one shot of `motion`
    vignette: bool = False
    fonts_dir: str | None = None  # relative to the working dir, for the on-screen text font
    video: Path | None = None  # a real clip (Google Flow / Veo) used instead of the still image + camera move
    atmosphere: str = ""  # rain / snow / fire / storm (services/atmosphere.py)
    seed: int = 0
    living: Path | None = None  # seamless loop of the still with swaying plants / dancing fire (services/living.py)


def video_base_graph(spec: ClipSpec, label: str = "base") -> str:
    """The scene's picture from a video file: fill the frame, constant fps, first `duration` seconds
    (the last frame is held if the clip is shorter than the line). Its own sound is ignored."""
    w, h = spec.size
    return (f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,crop={w}:{h},setsar=1,fps={FPS},"
            f"tpad=stop_mode=clone:stop_duration={spec.duration:.3f},trim=duration={spec.duration:.3f},"
            f"setpts=PTS-STARTPTS,settb=1/{FPS},format=yuv420p[{label}]")


def last_frame_cmd(exe: str, video: Path, out: Path, at: float) -> list[str]:
    """One still from the video (what the next scene's transition starts from)."""
    return [exe, "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{max(0.0, at):.3f}", "-i", str(video),
            "-frames:v", "1", str(out)]


def _scale(spec: ClipSpec) -> str:
    w, h = spec.size
    return f"scale={int(w * spec.prescale) // 2 * 2}:{int(h * spec.prescale) // 2 * 2}:flags=lanczos"


def _zoompan(spec: ClipSpec, motion: str, frames: int, hook: bool, out_frames: int, offset: int = 0,
             moving: bool = False) -> str:
    """`moving` = the input is a video (a living loop): one output frame per input frame, cut to `out_frames`."""
    w, h = spec.size
    z, x, y = zoompan_expr(motion, frames, hook, offset)
    if moving:
        return (f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s={w}x{h}:fps={FPS},trim=end_frame={out_frames},"
                f"setpts=PTS-STARTPTS,fps={FPS},settb=1/{FPS},setsar=1,format=yuv420p")
    return f"zoompan=z='{z}':x='{x}':y='{y}':d={out_frames}:s={w}x{h}:fps={FPS},setsar=1,format=yuv420p"


def _kenburns(label_in: str, label_out: str, spec: ClipSpec, motion: str, frames: int, hook: bool,
              out_frames: int, offset: int = 0) -> str:
    return f"[{label_in}]{_scale(spec)},{_zoompan(spec, motion, frames, hook, out_frames, offset)}[{label_out}]"


def clip_shots(spec: ClipSpec) -> list[tuple[str, int]]:
    return spec.shots or [(spec.motion, frame_count(spec.duration))]


def scene_clip_cmd(exe: str, spec: ClipSpec) -> list[str]:
    frames = frame_count(spec.duration)
    living = spec.living if spec.living and not spec.video else None
    source = ["-stream_loop", "-1", "-i", str(living)] if living else ["-i", str(spec.video or spec.image)]
    cmd = [exe, "-y", "-hide_banner", "-loglevel", "error", *source, "-i", str(spec.audio)]
    nxt = 2
    shots = clip_shots(spec)
    if spec.video:
        graph = [video_base_graph(spec)]
    elif len(shots) == 1:
        graph = [f"[0:v]{_scale(spec)},{_zoompan(spec, shots[0][0], frames, spec.hook, frames, moving=bool(living))}"
                 f"[base]"]
    else:  # a long scene: same picture, cut to a second framing at a word boundary (jump cut)
        names = "".join(f"[s{k}]" for k in range(len(shots)))
        graph = [f"[0:v]{_scale(spec)},split={len(shots)}{names}"]
        for k, (motion, n) in enumerate(shots):
            graph.append(f"[s{k}]{_zoompan(spec, motion, n, False, n, moving=bool(living))}[k{k}]")
        # concat outputs a microsecond timebase; xfade needs the same 1/FPS as the previous scene's tail
        graph.append("".join(f"[k{k}]" for k in range(len(shots))) + f"concat=n={len(shots)}:v=1:a=0,settb=1/{FPS}[base]")
    vlabel = "base"
    if spec.transition and spec.prev_image:
        tdur = spec.transition_sec or transition_duration(spec.transition)
        tframes = max(2, round(tdur * FPS))
        cmd += ["-i", str(spec.prev_image)]
        graph.append(_kenburns(f"{nxt}:v", "prev", spec, spec.prev_motion, spec.prev_frames, spec.prev_hook,
                               tframes, offset=max(1, spec.prev_frames - 1)))
        graph.append(f"[prev][base]xfade=transition={spec.transition}:duration={tframes / FPS:.3f}:offset=0[xf]")
        vlabel = "xf"
        nxt += 1
    if spec.atmosphere and not spec.video:
        from . import atmosphere

        loop = atmosphere.overlay_path(spec.atmosphere)
        fx_input = None
        if loop:
            cmd += ["-stream_loop", "-1", "-i", str(loop)]
            fx_input, nxt = nxt, nxt + 1
        graph += atmosphere.graph(spec.atmosphere, vlabel, "atm", fx_input, spec.size, spec.seed)
        vlabel = "atm"
    post = []
    if spec.fade_in:
        post.append(f"fade=t=in:st=0:d={FADE_IN_SEC}")
    if spec.fade_out:
        post.append(f"fade=t=out:st={max(0.0, spec.duration - FADE_OUT_SEC):.3f}:d={FADE_OUT_SEC}")
    if spec.vignette:
        post.append(VIGNETTE)
    if spec.subtitles:
        post.append(f"ass={spec.subtitles}" + (f":fontsdir={spec.fonts_dir}" if spec.fonts_dir else ""))
    graph.append(f"[{vlabel}]{','.join(post) or 'null'}[v]")

    fmt = "aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo"
    graph.append(f"[1:a]{fmt},{VOICE_FX},apad=whole_dur={spec.duration:.3f}[voice]")
    mix = ["[voice]"]
    for k, hit in enumerate(spec.sfx):
        cmd += ["-i", str(hit.path)]
        ms = int(round(hit.delay * 1000))
        graph.append(f"[{nxt}:a]{fmt},volume={hit.volume:.2f}" + (f",adelay={ms}|{ms}" if ms else "") + f"[fx{k}]")
        mix.append(f"[fx{k}]")
        nxt += 1
    if len(mix) > 1:
        graph.append(f"{''.join(mix)}amix=inputs={len(mix)}:duration=first:normalize=0,{LIMITER}[a]")
    else:
        graph.append(f"[voice]{LIMITER}[a]")
    cmd += ["-filter_complex", ";".join(graph), "-map", "[v]", "-map", "[a]", "-t", f"{spec.duration:.3f}",
            "-r", str(FPS), *spec.codec_args]
    if spec.threads:
        cmd += ["-threads", str(spec.threads)]
    # PCM audio in a .mov: no AAC priming gaps at the joins, and only one lossy encode (final mix)
    cmd += ["-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", str(spec.out)]
    return cmd


def concat_list(paths: list[Path]) -> str:
    lines = []
    for p in paths:
        s = Path(p).resolve().as_posix().replace("'", "'\\''")
        lines.append(f"file '{s}'")
    return "\n".join(lines) + "\n"


def concat_cmd(exe: str, list_file: Path, out: Path) -> list[str]:
    return [exe, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(list_file),
            "-c", "copy", str(out)]


def music_mix_cmd(exe: str, video: Path, out: Path, total: float, music: Path | None, music_db: float = MUSIC_DB,
                  duck: bool = True, loudnorm: bool = True, music_start: float = 0.0,
                  gain_expr: str | None = None) -> list[str]:
    """Final audio: music (looped, faded) ducked under the narration with a sidechain compressor,
    then the whole mix normalized to LOUDNESS_LUFS. Video is stream-copied."""
    cmd = [exe, "-y", "-hide_banner", "-loglevel", "error", "-i", str(video)]
    voice = "[0:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo"
    master = f"loudnorm=I={LOUDNESS_LUFS}:TP=-1.5:LRA=11,aresample=48000" if loudnorm else LIMITER
    if not music:
        graph = f"{voice},{master}[a]"
    else:
        fade_start = max(0.0, total - 3.0)
        cmd += ["-stream_loop", "-1", "-i", str(music)]
        ms = int(round(music_start * 1000))
        mus = (f"[1:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,volume={music_db}dB,"
               + (f"adelay={ms}|{ms},afade=t=in:st={music_start:.2f}:d=0.6," if ms else "afade=t=in:d=2,")
               + (f"volume='{gain_expr}':eval=frame," if gain_expr else "")
               + f"afade=t=out:st={fade_start:.2f}:d=3")
        if duck:
            graph = (f"{voice},asplit=2[vo][sc];{mus}[m];"
                     f"[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[duck];"
                     f"[vo][duck]amix=inputs=2:duration=first:normalize=0,{master}[a]")
        else:
            graph = f"{voice}[vo];{mus}[m];[vo][m]amix=inputs=2:duration=first:normalize=0,{master}[a]"
    return cmd + ["-filter_complex", graph, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac",
                  "-b:a", "192k", "-t", f"{total:.3f}", "-movflags", "+faststart", str(out)]


# ------------------------------------------------------------------ helpers
def file_sig(path: Path | None) -> str:
    if not path:
        return "-"
    st = Path(path).stat()
    return f"{Path(path).name}:{st.st_size}:{int(st.st_mtime)}"


def clip_hash(spec: ClipSpec, narration: str) -> str:
    """`narration` = the scene's subtitle file text (so caption or CTA changes re-render the clip)."""
    raw = "|".join([RENDER_VERSION, file_sig(spec.image), file_sig(spec.audio), spec.motion,
                    str(spec.hook), f"{spec.duration:.3f}", str(spec.size), " ".join(spec.codec_args),
                    ";".join(f"{file_sig(s.path)}@{s.volume:.2f}+{s.delay:.2f}" for s in spec.sfx),
                    f"{spec.transition}:{spec.transition_sec}", file_sig(spec.prev_image) if spec.transition else "-",
                    f"{spec.prev_motion}:{spec.prev_frames}:{spec.prev_hook}" if spec.transition else "-",
                    f"fi{spec.fade_in}fo{spec.fade_out}", str(clip_shots(spec)), f"vg{spec.vignette}",
                    narration if spec.subtitles else "", "subs" if spec.subtitles else "nosubs",
                    *([f"video:{file_sig(spec.video)}"] if spec.video else []),
                    *([f"atm:{spec.atmosphere}:{spec.seed}"] if spec.atmosphere else []),
                    *([f"live:{file_sig(spec.living)}"] if spec.living and not spec.video else [])])
    return hashlib.sha1(raw.encode()).hexdigest()


def placeholder_image(path: Path, order: int, text: str) -> Path:
    """Colourful card used when a scene has no image yet (the render must never fail for that)."""
    from PIL import Image, ImageDraw, ImageFont

    palette = [(124, 58, 237), (79, 70, 229), (14, 165, 233), (16, 185, 129), (249, 115, 22), (236, 72, 153)]
    c = palette[order % len(palette)]
    img = Image.new("RGB", (1920, 1080), c)
    d = ImageDraw.Draw(img)
    try:
        big = ImageFont.truetype("arial.ttf", 220)
        small = ImageFont.truetype("arial.ttf", 54)
    except OSError:  # no Arial (Linux): Pillow's built-in scalable font
        big, small = ImageFont.load_default(size=220), ImageFont.load_default(size=54)
    d.text((960, 430), str(order), fill="white", font=big, anchor="mm")
    d.text((960, 700), (text[:70] + "...") if len(text) > 70 else text, fill="white", font=small, anchor="mm")
    img.save(path)
    return path


def media_duration(path: Path) -> float:
    from .media_library import audio_duration

    return audio_duration(path)


# ------------------------------------------------------------------ orchestration
def project_work_dir(project) -> Path:
    from .files import project_media_dir

    d = project_media_dir(project.pk) / "render"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _ensure_sound_library(media_library) -> None:
    """Transitions and cues need sounds: if the library has no SFX or no music yet, load the bundled
    CC0 starter pack once (already-imported items are skipped)."""
    from ..models import MusicTrack, SoundEffect

    if (SoundEffect.objects.exists() and MusicTrack.objects.exists()) or not media_library.starter_pack_available():
        return
    try:
        m, s = media_library.import_starter_pack()
        logger.info("Starter sound library imported for rendering: %s music, %s sfx", m, s)
    except Exception as exc:  # noqa: BLE001 - a missing sound must never stop the render
        logger.warning("Starter pack import failed: %s", exc)


def _render_clip(exe: str, spec: ClipSpec, final: Path, cwd: Path) -> None:
    spec.out = final.with_name(final.stem + ".part.mov")
    _run(scene_clip_cmd(exe, spec), cwd=cwd)
    spec.out.replace(final)
    spec.out = final


def scene_dub_cmd(exe: str, spec: ClipSpec, voice: Path, out: Path) -> list[str]:
    """Audio only: a dubbed line (sped up to fit the scene when longer) + the scene's own SFX, as a PCM wav."""
    length = media_duration(voice) or 0.0
    window = max(0.5, spec.duration - 0.15)
    tempo = min(1.6, length / window) if length > window else 1.0
    fmt = "aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo"
    cmd = [exe, "-y", "-hide_banner", "-loglevel", "error", "-i", str(voice)]
    speed = f"atempo={tempo:.3f}," if tempo > 1.0 else ""
    graph = [f"[0:a]{fmt},{speed}{VOICE_FX},apad=whole_dur={spec.duration:.3f}[voice]"]
    mix = ["[voice]"]
    for k, hit in enumerate(spec.sfx, start=1):
        cmd += ["-i", str(hit.path)]
        ms = int(round(hit.delay * 1000))
        graph.append(f"[{k}:a]{fmt},volume={hit.volume:.2f}" + (f",adelay={ms}|{ms}" if ms else "") + f"[fx{k}]")
        mix.append(f"[fx{k}]")
    graph.append(f"{''.join(mix)}amix=inputs={len(mix)}:duration=first:normalize=0,{LIMITER}[a]" if len(mix) > 1
                 else f"[voice]{LIMITER}[a]")
    return cmd + ["-filter_complex", ";".join(graph), "-map", "[a]", "-t", f"{spec.duration:.3f}",
                  "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", str(out)]


def render_project(project, quality: str = "final", progress=lambda msg: None,
                   captions: bool = True, dub_audio: dict | None = None, dub_out: Path | None = None) -> tuple[Path, float]:
    """Plan every scene clip (DB work on this thread), render missing ones in parallel,
    concat, mix music. Returns (mp4 path, duration)."""
    from . import cta, media_library, overlays, subtitles

    exe = ffmpeg_exe()
    caps = capabilities()
    q = QUALITIES[quality]
    codec = video_codec_args(quality, caps)
    workers = render_workers()
    threads = max(1, (os.cpu_count() or 2) // workers)
    label = "720p" if quality == "preview" else "1080p"
    work = project_work_dir(project)
    clips_dir = work / f"clips_{quality}"
    clips_dir.mkdir(exist_ok=True)
    scenes = list(project.scenes.order_by("order"))
    if not scenes:
        raise RenderError("Sahnalar yo'q — avval ssenariy kerak.")
    missing_audio = [s.order for s in scenes if not s.audio]
    if missing_audio:
        raise RenderError(f"Bu sahnalarda ovoz yo'q: {missing_audio[:15]}. Avval ovozni yarating.")

    progress(f"Montaj ({label}): sahnalar rejalashtirilmoqda...")
    _ensure_sound_library(media_library)
    plan: list[tuple[object, ClipSpec, Path, str]] = []
    total = 0.0
    used_jarring: set[str] = set()
    prev: dict | None = None
    voice_lens = [s.audio_duration or media_duration(Path(s.audio.path)) for s in scenes]
    # PAD after every line, plus the director's dramatic pause where there is one
    n_hook = next((i for i, s in enumerate(scenes) if s.beat_type != "hook"), len(scenes))
    pads = [HOOK_PAD if i < n_hook - 1 else PAD for i in range(len(scenes))]  # tight hook, normal pause after it
    durations = [round(v + p + (s.pause_after_ms or 0) / 1000, 3) for v, p, s in zip(voice_lens, pads, scenes)]
    cta_plan = cta.plan(durations, [s.beat_type for s in scenes], [s.narration for s in scenes]) if caps["ass"] else {}
    like_plan = cta.plan_likes(durations, [s.narration for s in scenes], cta_plan) if cta_plan else {}
    starts = [round(sum(durations[:i]), 3) for i in range(len(scenes))]
    vignette = bool(getattr(settings, "VIGNETTE", True))
    fonts_dir = None
    if caps["ass"] and overlays.FONT_FILE.exists():  # the on-screen text font, next to the .ass files
        (clips_dir / "fonts").mkdir(exist_ok=True)
        target = clips_dir / "fonts" / overlays.FONT_FILE.name
        if not target.exists():
            shutil.copyfile(overlays.FONT_FILE, target)
        fonts_dir = "fonts"
    prev_motion = ""
    for i, scene in enumerate(scenes):
        audio = Path(scene.audio.path)
        voice_len = voice_lens[i]
        duration = durations[i]
        image = Path(scene.image.path) if scene.image else placeholder_image(work / f"placeholder_{scene.order:03d}.png",
                                                                               scene.order, scene.narration)
        hook = scene.beat_type == "hook"
        motion = motion_for_scene(i, scene, prev_motion)
        shots = shot_list(motion, duration, split_points(duration, voice_len, scene.subtitle_words, hook))
        video = Path(scene.video.path) if scene.video and Path(scene.video.path).exists() else None
        if video:  # a real clip: the next transition starts from a frame of it, not from the still
            frame = work / f"vframe_{scene.order:03d}_{int(video.stat().st_mtime)}_{int(duration * 10)}.png"
            if not frame.exists():
                length = media_duration(video) or duration
                _run(last_frame_cmd(exe, video, frame, min(duration, length) - 0.1))
            image, shots, motion = frame, [("none", frame_count(duration))], "none"
        transition = plan_transition(i, scene, used_jarring) if caps.get("xfade", True) else ""
        whip = scene.transition_in == "whip"
        if i == n_hook and 0 < n_hook < len(scenes) and not transition and caps.get("xfade", True):
            transition, whip = "smoothleft", True  # the hook ends with a fast whip into the main part
        hits: list[SfxHit] = []
        items = scene_sfx_items(scene)
        for k, item in enumerate(items):
            fx = media_library.pick_sfx(item["tag"], seed=scene.order + k)
            if fx:
                hits.append(SfxHit(Path(fx.file.path), db_to_gain(item["gain_db"]),
                                   min(item["offset_ms"] / 1000, max(0.0, duration - 0.3))))
        tr_tag = transition_sfx_tag(transition, [x["tag"] for x in items])
        tr_fx = media_library.pick_sfx(tr_tag, seed=i) if tr_tag else None
        if tr_fx:
            hits.append(SfxHit(Path(tr_fx.file.path), FLASH_SFX_VOLUME if transition in FLASH_TRANSITIONS
                               else TRANSITION_SFX_VOLUME))
        if i == 1 and n_hook and not items:  # music drops in after the first line: a soft hit with it
            fx = media_library.pick_sfx("impact", seed=1)
            if fx:
                hits.append(SfxHit(Path(fx.file.path), db_to_gain(HOOK_IMPACT_DB), 0.0))
        if i == n_hook - 1 and 0 < n_hook < len(scenes):  # a riser that peaks exactly at the end of the hook
            fx = media_library.pick_sfx("riser", seed=0)
            if fx:
                hits.append(SfxHit(Path(fx.file.path), db_to_gain(HOOK_RISER_DB),
                                   max(0.0, duration - (fx.duration or 2.0) - 0.05)))
        if scene.music_cue == "stinger" and not items:
            fx = media_library.pick_sfx("impact", seed=i)
            if fx:
                hits.append(SfxHit(Path(fx.file.path), db_to_gain(-10.0), 0.0))
        if i in cta_plan:  # "Subscribe" button animation: pop / click / click / ding
            for snd in cta.SOUNDS:
                fx = media_library.pick_sfx(snd.tag, seed=0)
                if fx:
                    hits.append(SfxHit(Path(fx.file.path), snd.volume, cta_plan[i] + snd.delay))
        if i in like_plan:  # "Like" button animation: pop / click
            for snd in cta.LIKE_SOUNDS:
                fx = media_library.pick_sfx(snd.tag, seed=1)
                if fx:
                    hits.append(SfxHit(Path(fx.file.path), snd.volume, like_plan[i] + snd.delay))
        subs_name = None
        ass_text = ""
        if caps["ass"]:
            subs_name = f"subs_{quality}_{scene.order:03d}.ass"
            # captions=False: no spoken-word subtitles; on-screen key texts and the subscribe animation stay
            ass_text = (subtitles.scene_ass(scene.narration, voice_len, scene.subtitle_words, hook=hook)
                        if captions else subtitles.ASS_HEADER)
            if scene.on_screen_text:
                ass_text += "".join(overlays.events(scene.on_screen_text, duration))
            if i in cta_plan:
                ass_text += "".join(cta.events(cta_plan[i]))
            if i in like_plan:
                ass_text += "".join(cta.like_events(like_plan[i]))
            (clips_dir / subs_name).write_text(ass_text, encoding="utf-8")
        spec = ClipSpec(image=image, audio=audio, out=Path(), duration=duration, motion=motion,
                        size=q["size"], prescale=q["prescale"], codec_args=codec, hook=False, sfx=hits,
                        subtitles=subs_name, fade_in=i == 0, fade_out=i == len(scenes) - 1, threads=threads,
                        shots=shots, vignette=vignette, fonts_dir=fonts_dir if scene.on_screen_text else None,
                        video=video)
        if getattr(settings, "ATMOSPHERE", True):
            from . import atmosphere

            spec.atmosphere, spec.seed = atmosphere.effect_for(scene), scene.order
        if getattr(settings, "LIVING_PICTURES", True) and not video and scene.image and dub_audio is None:
            from . import living

            spec.living = living.loop_path(scene)
        if transition and prev:
            spec.transition = transition
            spec.transition_sec = transition_duration(transition, whip=whip)
            spec.prev_image, spec.prev_motion = prev["image"], prev["motion"]
            spec.prev_frames, spec.prev_hook = prev["frames"], prev["hook"]
        h = clip_hash(spec, ass_text or scene.narration)
        final = clips_dir / f"scene_{scene.order:03d}_{h[:12]}.mov"
        plan.append((scene, spec, final, h))
        last_motion, last_frames = clip_shots(spec)[-1]
        prev = {"image": image, "motion": last_motion, "frames": last_frames, "hook": False}
        prev_motion = motion
        total += duration

    if dub_audio is not None:  # a dubbed audio track: same timing, SFX and music; no video work
        return _render_dub(project, exe, plan, scenes, starts, durations, n_hook, total, dub_audio, dub_out, caps, workers,
                           progress)

    todo = [(spec, final) for _, spec, final, _ in plan if not final.exists()]
    if todo:
        progress(f"Montaj ({label}): 0/{len(todo)} sahna ({workers} ta parallel)")
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(_render_clip, exe, spec, final, clips_dir) for spec, final in todo]
            try:
                for n, fut in enumerate(as_completed(futures), start=1):
                    fut.result()
                    progress(f"Montaj ({label}): {n}/{len(todo)} sahna tayyor")
            except BaseException:
                for f in futures:
                    f.cancel()
                raise

    for scene, spec, final, h in plan:
        spec.out = final
        if quality == "final" and scene.clip_hash != h:
            type(scene).objects.filter(pk=scene.pk).update(clip_hash=h)

    used = {final.name for _, _, final, _ in plan}
    for old in clips_dir.glob("scene_*"):  # drop clips of scenes that changed (and old v1 .mp4 clips)
        if old.name not in used:
            old.unlink(missing_ok=True)

    progress("Sahnalar birlashtirilmoqda...")
    list_file = work / f"concat_{quality}.txt"
    list_file.write_text(concat_list([final for _, _, final, _ in plan]), encoding="utf-8")
    joined = work / f"joined_{quality}.mov"
    _run(concat_cmd(exe, list_file, joined))

    progress("Musiqa va ovoz balansi (ducking, -14 LUFS)...")
    out = work / f"{quality}.mp4"
    music, music_start, gain = _music_plan(project, scenes, starts, durations, n_hook)
    _run(music_mix_cmd(exe, joined, out, total, Path(music.file.path) if music else None,
                       duck=caps.get("duck", True), loudnorm=caps.get("loudnorm", True),
                       music_start=music_start, gain_expr=gain))
    out.with_suffix(".srt").write_text(subtitles.srt_for_scenes(
        [(starts[i], s.narration, voice_lens[i], s.subtitle_words) for i, s in enumerate(scenes)]), encoding="utf-8")
    joined.unlink(missing_ok=True)
    return out, round(total, 2)


def _music_plan(project, scenes, starts, durations, n_hook):
    from . import media_library

    music = project.music_track
    if music is None:
        mood = (project.script_json or {}).get("mood") or (project.niche.default_mood if project.niche else None)
        music = media_library.pick_music(mood, exclude_project_id=project.pk)
        if music:
            type(project).objects.filter(pk=project.pk).update(music_track=music)
    windows = []
    for i, scene in enumerate(scenes):
        a, b = starts[i], starts[i] + durations[i]
        if scene.music_cue == "drop_out":  # silence under the line before a reveal
            windows.append((max(0.0, a - 0.2), b, DROP_OUT_LEVEL, 0.4))
        elif scene.music_cue == "swell":
            windows.append((a, b, SWELL_LEVEL, 1.0))
        elif scene.music_cue == "change_mood":  # a short dip marks the turn
            windows.append((a, a + 1.2, MOOD_DIP_LEVEL, 0.3))
    music_start = durations[0] if n_hook and len(scenes) > 1 else 0.0  # music enters after the first line
    return music, music_start, music_gain_expr(windows)


def _render_dub(project, exe, plan, scenes, starts, durations, n_hook, total, dub_audio, dub_out, caps, workers, progress):
    work = Path(dub_out).parent / (Path(dub_out).stem + "_parts")
    work.mkdir(parents=True, exist_ok=True)
    parts = []
    jobs = []
    for scene, spec, _final, _h in plan:
        part = work / f"scene_{scene.order:03d}.wav"
        parts.append(part)
        jobs.append(scene_dub_cmd(exe, spec, Path(dub_audio[scene.order]), part))
    with ThreadPoolExecutor(max_workers=max(2, workers)) as pool:
        for n, _ in enumerate(pool.map(_run, jobs), start=1):
            if n % 20 == 0:
                progress(f"Dublyaj: {n}/{len(jobs)} sahna")
    list_file = work / "concat.txt"
    list_file.write_text(concat_list(parts), encoding="utf-8")
    joined = work / "joined.wav"
    _run(concat_cmd(exe, list_file, joined))
    music, music_start, gain = _music_plan(project, scenes, starts, durations, n_hook)
    cmd = music_mix_cmd(exe, joined, Path(dub_out), total, Path(music.file.path) if music else None,
                        duck=caps.get("duck", True), loudnorm=caps.get("loudnorm", True),
                        music_start=music_start, gain_expr=gain)
    i = cmd.index("-map")
    del cmd[i:i + 2]  # no video stream in a wav
    j = cmd.index("-c:v")
    del cmd[j:j + 2]
    _run(cmd)
    shutil.rmtree(work, ignore_errors=True)
    return Path(dub_out), round(total, 2)
