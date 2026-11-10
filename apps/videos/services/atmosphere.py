"""Atmosphere effects: moving weather and light over a still picture, so it feels alive (owner, 2026-10-26).

rain / snow: a seamless 3-second loop of falling particles with alpha (drawn once with Pillow, cached in media/fx/),
overlaid on the scene. fire: the picture's light flickers like a campfire. storm: rain plus short lightning flashes.
The effect is picked from the scene's image prompt and narration (`effect_for`); scenes with a real video clip get none.
"""
from __future__ import annotations

import math
import random
import re
import subprocess
from pathlib import Path

from django.conf import settings

LOOP_FRAMES = 72  # 3 s at 24 fps; particle speeds are chosen so the loop is seamless
SIZE = (1920, 1080)
VERSION = "3"

KEYWORDS = [  # first match wins
    ("storm", r"\b(lightning|thunder\w*|storms?)\b"),
    ("rain", r"\b(rain\w*|drizzle|downpour|raindrops?|drips?|dripping)\b"),
    ("snow", r"\b(snow\w*|blizzard|frost\w*|snowflakes?)\b"),
    ("fire", r"\b(fire|fires|campfire|flames?|hearth|embers?|torch\w*|bonfire)\b"),
]
EFFECTS = {name for name, _ in KEYWORDS}
# under a roof the weather is only outside: no falling particles over the picture (a fire inside still flickers)
INDOOR = r"\b(window|inside|indoors?|room|bed|cave|caves|hut|huts|shelter|overhang|tent|under a hide|under one hide)\b"


def effect_for(scene) -> str:
    """'' or one of rain / snow / fire / storm, from what the picture shows (the prompt) first, then the line."""
    prompt = (scene.image_prompt or "").lower()
    indoor = bool(re.search(INDOOR, prompt))
    for text in (prompt, (scene.narration or "").lower()):
        for name, pattern in KEYWORDS:
            if indoor and name in ("rain", "snow"):
                continue
            if re.search(pattern, text):
                return "fire" if indoor and name == "storm" else name
    return ""


def fx_dir() -> Path:
    d = Path(settings.MEDIA_ROOT) / "fx"
    d.mkdir(parents=True, exist_ok=True)
    return d


def overlay_path(effect: str) -> Path | None:
    """The cached alpha loop for rain/snow (storm uses rain), drawn on first use."""
    kind = {"rain": "rain", "storm": "rain", "snow": "snow"}.get(effect)
    if not kind:
        return None
    out = fx_dir() / f"{kind}_v{VERSION}.mov"
    if not out.exists():
        _draw_loop(kind, out)
    return out


def _draw_loop(kind: str, out: Path) -> None:
    from PIL import Image, ImageDraw

    from .render import ffmpeg_exe

    w, h = SIZE
    rnd = random.Random(7)
    frames_dir = out.with_suffix("")
    frames_dir.mkdir(exist_ok=True)
    if kind == "rain":  # each drop falls 2 or 3 screen heights per loop: seamless
        drops = [(rnd.uniform(0, w), rnd.uniform(0, h), rnd.choice((2, 3)), rnd.uniform(28, 60), rnd.randint(70, 140))
                 for _ in range(260)]
    else:  # snow: one screen height per loop, sideways sway with a period of the loop
        drops = [(rnd.uniform(0, w), rnd.uniform(0, h), 1, rnd.uniform(5, 11), rnd.randint(190, 250))
                 for _ in range(220)]
    for f in range(LOOP_FRAMES):
        img = Image.new("RGBA", SIZE, (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        for k, (x, y, laps, size, alpha) in enumerate(drops):
            yy = (y + f * laps * h / LOOP_FRAMES) % h
            if kind == "rain":
                seg = [(x, yy), (x - size * 0.18, yy + size)]  # dark edge + light core: visible on light and dark pictures
                d.line(seg, fill=(40, 60, 90, alpha // 2), width=4)
                d.line(seg, fill=(225, 235, 255, alpha), width=2)
            else:
                xx = (x + 18 * math.sin(2 * math.pi * (f / LOOP_FRAMES + k / 13))) % w
                d.ellipse([xx - size / 2, yy - size / 2, xx + size / 2, yy + size / 2], fill=(255, 255, 255, alpha),
                          outline=(90, 110, 140, alpha // 2), width=2)
        img.save(frames_dir / f"f{f:03d}.png")
    subprocess.run([ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error", "-framerate", "24", "-i",
                    str(frames_dir / "f%03d.png"), "-c:v", "png", "-pix_fmt", "rgba", str(out)], check=True)
    for p in frames_dir.glob("*.png"):
        p.unlink()
    frames_dir.rmdir()


def light_filter(effect: str, seed: int = 0) -> str:
    """Brightness animation for the picture itself ('' when none)."""
    if effect == "fire":  # two out-of-step waves: an irregular, warm flicker
        return (f"eq=brightness='0.035*sin(2*PI*t*1.7+{seed % 7})+0.02*sin(2*PI*t*4.3+{seed % 5})':"
                "saturation=1.06:eval=frame")
    if effect == "storm":  # a short flash every few seconds, at a different moment per scene
        period = 3.4 + (seed % 5) * 0.4
        return f"eq=brightness='if(lt(mod(t+{seed % 3}.3,{period:.1f}),0.09),0.32,0)':eval=frame"
    return ""


def graph(effect: str, in_label: str, out_label: str, fx_input: int | None, size: tuple[int, int], seed: int = 0) -> list[str]:
    """filter_complex parts that take [in_label] to [out_label]; fx_input is the looped overlay's input index."""
    parts, cur = [], in_label
    light = light_filter(effect, seed)
    if light:
        parts.append(f"[{cur}]{light}[atl]")
        cur = "atl"
    if fx_input is not None:
        w, h = size
        parts.append(f"[{fx_input}:v]scale={w}:{h},format=rgba,colorchannelmixer=aa=0.75[atfx]")
        parts.append(f"[{cur}][atfx]overlay=0:0:shortest=1:format=auto,format=yuv420p[{out_label}]")
    else:
        parts.append(f"[{cur}]null[{out_label}]")
    return parts
