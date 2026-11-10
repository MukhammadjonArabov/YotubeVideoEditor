"""Small template helpers for the AutoExplainer UI."""
from __future__ import annotations

import zlib

from django import template

register = template.Library()


@register.filter
def tagclass(tag: str) -> str:
    """Stable colour class for a tag (t0..t5)."""
    return f"t{zlib.crc32(str(tag).lower().encode()) % 6}"


@register.filter
def compact(n) -> str:
    """8744094 -> 8.7M, 14665 -> 14.7K."""
    try:
        n = float(n or 0)
    except (TypeError, ValueError):
        return "—"
    for div, suf in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if n >= div:
            v = n / div
            return f"{v:.1f}".rstrip("0").rstrip(".") + suf
    return str(int(n))


@register.filter
def mmss(seconds) -> str:
    try:
        s = int(round(float(seconds or 0)))
    except (TypeError, ValueError):
        return "—"
    return f"{s // 60}:{s % 60:02d}"
