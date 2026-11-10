"""Living pictures (owner, 2026-10-30): grass and leaves sway in the wind and flames dance, the rest stays still.

From each still a seamless 4-second loop (cinemagraph) is made once and cached in media/projects/p<id>/living/:
- vegetation (green / yellow-green, saturated) gets a slow wind field: small, smooth sideways waves, stronger
  higher up in a plant, so tips move and roots stay put;
- fire (bright, saturated orange-yellow) gets an upward flickering turbulence and a light flicker of its glow.
People and objects are not in those masks, so their shape never changes. Every motion repeats a whole number of times
per loop, so the loop has no jump. The render plays the loop under its usual camera move (render.scene_clip_cmd).
"""
from __future__ import annotations

import hashlib
import logging
import subprocess
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

VERSION = "2"
LOOP_SEC = 4
FPS = 30
MIN_SHARE = 0.01  # less moving area than this: not worth a loop
WIND_PX = 4.5  # sway at the tips of a plant
FIRE_PX = 4.0


def masks(img: np.ndarray):
    """-> (vegetation 0..1, fire 0..1), soft-edged."""
    import cv2

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    # green leaves and grass, and dry yellow grass (hue 22+); skin and brown hide sit below hue 20
    veg = ((h >= 22) & (h <= 90) & (s >= 70) & (v >= 60)).astype(np.uint8) * 255
    veg = cv2.morphologyEx(veg, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    # a flame is very bright, strongly saturated orange-yellow around a white-hot core; lit skin, wood and dry grass
    # are less saturated or have no bright core, so they stay still
    warm = ((h <= 32) & (s >= 170) & (v >= 215)).astype(np.uint8) * 255
    core = ((v >= 250) & ((s < 120) | ((h >= 18) & (h <= 34)))).astype(np.uint8) * 255
    fire = cv2.morphologyEx(warm | (core & cv2.dilate(warm, np.ones((15, 15), np.uint8))), cv2.MORPH_CLOSE,
                            np.ones((5, 5), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(fire)
    keep = np.zeros_like(fire)
    area_max = img.shape[0] * img.shape[1] * 0.05
    for i in range(1, n):
        if not 80 < stats[i, cv2.CC_STAT_AREA] < area_max:
            continue
        if stats[i, cv2.CC_STAT_HEIGHT] < 0.45 * stats[i, cv2.CC_STAT_WIDTH]:  # flames stand up; sunlit grass lies flat
            continue
        comp = lab == i
        if (core[comp] > 0).mean() >= 0.08 and (v[comp] >= 240).mean() >= 0.3:
            keep[comp] = 255
    veg[cv2.dilate(keep, np.ones((25, 25), np.uint8)) > 0] = 0
    fire = cv2.dilate(keep, np.ones((9, 9), np.uint8))
    return (cv2.GaussianBlur(veg.astype(np.float32) / 255, (0, 0), 4),
            cv2.GaussianBlur(fire.astype(np.float32) / 255, (0, 0), 5))


def frames(img: np.ndarray, veg: np.ndarray, fire: np.ndarray, n: int):
    import cv2

    hgt, wid = img.shape[:2]
    yy, xx = np.mgrid[0:hgt, 0:wid].astype(np.float32)
    # how far up a plant a pixel is: plant pixels with more plant below them sway more (tips vs roots)
    col = np.cumsum((veg > 0.3)[::-1].astype(np.float32), axis=0)[::-1]
    height = np.clip(1.0 - col / 140.0, 0.25, 1.0)
    height = cv2.GaussianBlur(height * veg, (0, 0), 6)
    glow = cv2.GaussianBlur(fire, (0, 0), 40)
    glow = glow / max(1e-6, glow.max())
    for i in range(n):
        t = 2 * np.pi * i / n  # one full turn per loop: every term below is periodic in it
        wind = (0.65 * np.sin(t + xx * 0.010 + yy * 0.006) + 0.35 * np.sin(2 * t + xx * 0.027 - yy * 0.011 + 1.3))
        dx = WIND_PX * height * wind
        dy = 0.25 * WIND_PX * height * np.sin(2 * t + xx * 0.02)
        flick = np.sin(3 * t + yy * 0.09 + xx * 0.03) + 0.5 * np.sin(5 * t - yy * 0.05 + 2.0)
        dx += FIRE_PX * fire * flick * 0.6
        dy += FIRE_PX * fire * (0.8 + 0.5 * np.sin(4 * t + xx * 0.07))  # sample from below: flames lick upward
        out = cv2.remap(img, xx - dx, yy + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        if fire.max() > 0:
            gain = 1 + glow[..., None] * (0.06 * np.sin(5 * t) + 0.04 * np.sin(7 * t + 1.0))
            out = np.clip(out.astype(np.float32) * gain, 0, 255).astype(np.uint8)
        yield out


def loop_path(scene) -> Path | None:
    """The scene's living loop (made now if missing), or None when nothing in the picture should move."""
    if not scene.image:
        return None
    src = Path(scene.image.path)
    if not src.exists():
        return None
    sig = hashlib.sha1(f"{VERSION}|{src.name}|{src.stat().st_size}|{src.stat().st_mtime_ns}".encode()).hexdigest()[:12]
    folder = src.parent.parent / "living"
    out = folder / f"scene_{scene.order:03d}_{sig}.mp4"
    none_marker = out.with_suffix(".none")
    if out.exists():
        return out
    if none_marker.exists():
        return None
    try:
        return _make(src, out, none_marker)
    except Exception:  # never let a decoration break the render: fall back to the still
        logger.exception("Living loop failed for %s", src)
        return None


def _make(src: Path, out: Path, none_marker: Path) -> Path | None:
    import cv2
    from imageio_ffmpeg import get_ffmpeg_exe

    out.parent.mkdir(parents=True, exist_ok=True)
    img = cv2.imread(str(src))
    veg, fire = masks(img)
    if (veg > 0.3).mean() + (fire > 0.3).mean() < MIN_SHARE:
        none_marker.write_text("")
        return None
    hgt, wid = img.shape[:2]
    tmp = out.with_suffix(".part.mp4")
    enc = subprocess.Popen([get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{wid}x{hgt}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "fast",
                            "-crf", "14", "-pix_fmt", "yuv420p", str(tmp)], stdin=subprocess.PIPE)
    for fr in frames(img, veg, fire, LOOP_SEC * FPS):
        enc.stdin.write(fr.tobytes())
    enc.stdin.close()
    if enc.wait() != 0:
        raise RuntimeError("ffmpeg failed")
    tmp.replace(out)
    return out
