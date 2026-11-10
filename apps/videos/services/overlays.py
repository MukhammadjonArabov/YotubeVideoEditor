"""On-screen text for a scene (the director's `on_screen_text`), as ASS events burned into the clip.

One consistent, calm style so it reads as "edited", not "busy": a big condensed title (Bebas Neue)
in the upper third, popping in softly, with a thin accent line drawing out underneath, then fading.
Numbers count up ("200,000 YEARS" runs 0 -> 200,000), and percentages also fill a bar.
"""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from django.conf import settings

from .subtitles import ass_time

FONT_FILE = Path(settings.BASE_DIR) / "static" / "fonts" / "BebasNeue-Regular.ttf"
FONT_NAME = "Bebas Neue"
SIZE = 132
X, Y = 960, 215  # text centre (upper third: captions sit at the bottom, the subscribe button top-right)
WHITE, ACCENT, DARK = "&HFFFFFF&", "&H00D4FF&", "&H101010&"  # ASS colours are &HBBGGRR&
LEAD = 0.35  # appear this long after the scene starts (after the transition)
HOLD = 2.4  # seconds on screen at most
COUNT_SEC = 0.7  # count-up length
COUNT_STEPS = 14
NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")


@lru_cache(maxsize=256)
def text_width(text: str) -> float:
    try:
        from PIL import ImageFont

        return ImageFont.truetype(str(FONT_FILE), SIZE).getlength(text)
    except OSError:
        return len(text) * SIZE * 0.45


def _rect(w: float, h: float) -> str:
    w, h = int(w), int(h)
    return f"m 0 0 l {w} 0 l {w} {h} l 0 {h}"


def _count_values(target: float, steps: int) -> list[float]:
    """Ease-out count from 0 to target (fast start, gentle landing)."""
    return [target * (1 - (1 - k / steps) ** 3) for k in range(1, steps + 1)]


def _format_like(value: float, original: str) -> str:
    decimals = len(original.split(".")[1]) if "." in original else 0
    text = f"{value:,.{decimals}f}" if "," in original else f"{value:.{decimals}f}"
    return text


def percent_of(text: str) -> float | None:
    m = NUMBER.search(text)
    if m and ("%" in text or "PERCENT" in text.upper()):
        value = float(m.group().replace(",", ""))
        return value if 0 < value <= 100 else None
    return None


def events(text: str, scene_duration: float) -> list[str]:
    """ASS Dialogue lines for one scene's on-screen text (times relative to the scene start)."""
    text = " ".join((text or "").split()).upper()
    if not text or scene_duration < 1.2:
        return []
    start = LEAD
    end = min(scene_duration - 0.25, start + HOLD)
    style = (rf"\an5\pos({X},{Y})\fn{FONT_NAME}\fs{SIZE}\bord5\3c{DARK}\shad3\4a&H70&\4c{DARK}\fsp2")
    pop = r"\fad(140,220)\fscx86\fscy86\t(0,180,\fscx100\fscy100)"
    lines = []

    def add(layer: int, t0: float, t1: float, body: str) -> None:
        if t1 - t0 > 0.02:
            lines.append(f"Dialogue: {layer},{ass_time(t0)},{ass_time(t1)},Default,,0,0,0,,{body}\n")

    m = NUMBER.search(text)
    if m:  # count-up: the number runs from 0 to its value, the rest of the text stays put
        target = float(m.group().replace(",", ""))
        step = COUNT_SEC / COUNT_STEPS
        for k, v in enumerate(_count_values(target, COUNT_STEPS)):
            t0 = start + k * step
            t1 = start + (k + 1) * step if k + 1 < COUNT_STEPS else end
            first = r"\fad(140,0)\fscx86\fscy86\t(0,180,\fscx100\fscy100)" if k == 0 else ""
            last = r"\fad(0,220)" if k + 1 == COUNT_STEPS else ""
            number = rf"{{\1c{ACCENT}}}" + _format_like(v, m.group()) + rf"{{\1c{WHITE}}}"
            shown = text[:m.start()] + number + text[m.end():]
            add(20, t0, t1, rf"{{{style}\1c{WHITE}{first}{last}}}{shown}")
    else:
        add(20, start, end, rf"{{{style}\1c{WHITE}{pop}}}{text}")

    # accent line drawing out from the centre under the text
    width = min(1600.0, text_width(text) + 40)
    x0, y0 = X - width / 2, Y + SIZE * 0.42
    grow = (rf"\clip({int(X)},{int(y0) - 2},{int(X) + 1},{int(y0) + 12})"
            rf"\t(120,520,\clip({int(x0)},{int(y0) - 2},{int(x0 + width)},{int(y0) + 12}))")
    add(19, start, end, rf"{{\an7\pos({int(x0)},{int(y0)})\bord0\shad0\1c{ACCENT}\fad(0,220){grow}\p1}}{_rect(width, 8)}")

    pct = percent_of(text)
    if pct is not None:  # a bar that fills to the percentage
        bw, bh = 640, 22
        bx, by = X - bw / 2, Y + SIZE * 0.42 + 34
        fill = bx + bw * pct / 100
        add(18, start, end, rf"{{\an7\pos({int(bx)},{int(by)})\bord2\3c{DARK}\shad0\1c{WHITE}\1a&H90&\fad(140,220)\p1}}"
                            + _rect(bw, bh))
        add(19, start, end, rf"{{\an7\pos({int(bx)},{int(by)})\bord0\shad0\1c{ACCENT}\fad(0,220)"
                            rf"\clip({int(bx)},{int(by)},{int(bx) + 1},{int(by + bh)})"
                            rf"\t(150,{int(COUNT_SEC * 1000) + 150},\clip({int(bx)},{int(by)},{int(fill)},{int(by + bh)}))\p1}}"
                            + _rect(bw, bh))
    return lines


def font_dir() -> Path:
    return FONT_FILE.parent
