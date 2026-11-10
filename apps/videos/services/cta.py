"""Animated "Subscribe" call-to-action burned into a scene clip.

Drawn entirely with ASS vector shapes (no image assets): a red SUBSCRIBE button pops in at the
top-right corner (the image prompts keep that area empty sky), a cursor glides in and clicks it,
the button turns grey "SUBSCRIBED", the cursor clicks the bell, the bell rings, everything fades.
Sound: pop on appear, click on each press, ding on the bell.

Placement (render.py): once per video, on the scene where the narrator says "subscribe"; without such a
line, the first calm scene after SUBSCRIBE_CTA_AT_SEC (or the last scene, before the fade, for short videos).
A LIKE button animation follows the subscribe one (same scene when it is long enough, else the next scene) and plays
once more in the last scene where the narrator asks for a like.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from django.conf import settings

DURATION = 3.8  # seconds the whole animation takes
LEAD = 0.35  # start this long after the scene begins (after the transition)
MIN_SCENE = DURATION + LEAD + 0.2  # shorter scenes can't hold it

# Layout (ASS PlayRes 1920x1080)
BTN_X, BTN_Y = 1545, 120  # button centre
BTN_W, BTN_H, BTN_R = 380, 100, 22
BELL_X, BELL_Y = 1800, 120  # bell centre
RED, GREY, WHITE, BLACK = "&H0000FF&", "&H4A4A4A&", "&HFFFFFF&", "&H000000&"

# Timeline (ms from the CTA start)
T_IN = 0
T_CURSOR_IN, T_CLICK1 = 700, 1400
T_TO_BELL, T_CLICK2 = 1750, 2150
T_OUT = int(DURATION * 1000)


@dataclass
class CtaSound:
    tag: str
    delay: float  # seconds from the CTA start
    volume: float


SOUNDS = [CtaSound("pop", T_IN / 1000, 0.55), CtaSound("click", T_CLICK1 / 1000, 0.7),
          CtaSound("click", T_CLICK2 / 1000, 0.6), CtaSound("ding", (T_CLICK2 + 120) / 1000, 0.45)]


def enabled() -> bool:
    return bool(getattr(settings, "SUBSCRIBE_CTA", True))


def rounded_rect(w: int, h: int, r: int) -> str:
    """ASS drawing of a rounded rectangle (origin top-left)."""
    return (f"m {r} 0 l {w - r} 0 b {w} 0 {w} 0 {w} {r} l {w} {h - r} b {w} {h} {w} {h} {w - r} {h} "
            f"l {r} {h} b 0 {h} 0 {h} 0 {h - r} l 0 {r} b 0 0 0 0 {r} 0")


BELL = ("m 30 2 b 33 2 35 4 35 7 b 45 10 49 19 49 30 l 49 41 l 56 50 l 4 50 l 11 41 l 11 30 "
        "b 11 19 15 10 25 7 b 25 4 27 2 30 2 m 23 54 b 23 61 37 61 37 54")
CURSOR = "m 0 0 l 0 44 l 11 33 l 19 52 l 27 48 l 19 30 l 33 30"


def _t(ms: int) -> str:
    return str(max(0, int(ms)))


def ass_time(t: float) -> str:
    from .subtitles import ass_time as fmt

    return fmt(t)


def events(start: float) -> list[str]:
    """ASS Dialogue lines for one CTA starting `start` seconds into the scene."""
    s = start
    end = s + DURATION
    click_at = s + T_CLICK1 / 1000
    pop = r"\fscx60\fscy60\t(0,180,\fscx108\fscy108)\t(180,260,\fscx100\fscy100)"
    fade = rf"\fad(120,300)"
    shadow = rf"\shad4\4a&H80&\4c{BLACK}"
    lines = []

    def add(layer: int, t0: float, t1: float, text: str) -> None:
        lines.append(f"Dialogue: {layer},{ass_time(t0)},{ass_time(t1)},Default,,0,0,0,,{text}\n")

    rect = rounded_rect(BTN_W, BTN_H, BTN_R)
    # red SUBSCRIBE button (until the click), then grey SUBSCRIBED
    add(10, s, click_at, rf"{{\an5\pos({BTN_X},{BTN_Y})\bord0{shadow}\1c{RED}\fad(120,0){pop}\p1}}{rect}")
    add(11, s, click_at, rf"{{\an5\pos({BTN_X},{BTN_Y})\fnArial\b1\fs50\bord0\shad0\1c{WHITE}\fsp2\fad(120,0){pop}}}SUBSCRIBE")
    press = r"\fscx92\fscy92\t(0,140,\fscx100\fscy100)"
    add(10, click_at, end, rf"{{\an5\pos({BTN_X},{BTN_Y})\bord0{shadow}\1c{GREY}{fade}{press}\p1}}{rect}")
    add(11, click_at, end, rf"{{\an5\pos({BTN_X},{BTN_Y})\fnArial\b1\fs46\bord0\shad0\1c{WHITE}\fsp1{fade}{press}}}SUBSCRIBED")
    # bell: still, then rings after the second click
    ring_at = T_CLICK2 - 0
    swing = "".join(rf"\t({ring_at + k * 90},{ring_at + (k + 1) * 90},\frz{a})"
                    for k, a in enumerate([18, -16, 12, -9, 5, 0]))
    add(10, s, end, rf"{{\an5\pos({BELL_X},{BELL_Y})\org({BELL_X},{BELL_Y - 26})\bord3\3c{BLACK}\1c{WHITE}{shadow}{fade}"
                    rf"{pop}{swing}\p1}}{BELL}")
    # cursor: glides in from the lower right, presses the button, moves to the bell, presses it
    cx, cy = BTN_X + 40, BTN_Y + 10
    c_end = s + (T_CLICK2 + 650) / 1000
    clicks = (rf"\t({T_CLICK1 - T_CURSOR_IN - 60},{T_CLICK1 - T_CURSOR_IN + 60},\fscx82\fscy82)"
              rf"\t({T_CLICK1 - T_CURSOR_IN + 60},{T_CLICK1 - T_CURSOR_IN + 160},\fscx100\fscy100)"
              rf"\t({T_CLICK2 - T_CURSOR_IN - 60},{T_CLICK2 - T_CURSOR_IN + 60},\fscx82\fscy82)"
              rf"\t({T_CLICK2 - T_CURSOR_IN + 60},{T_CLICK2 - T_CURSOR_IN + 160},\fscx100\fscy100)")
    t_arrive = T_CLICK1 - T_CURSOR_IN - 150
    add(20, s + T_CURSOR_IN / 1000, s + T_TO_BELL / 1000,
        rf"{{\an7\move({cx + 260},{cy + 330},{cx},{cy},0,{_t(t_arrive)})\bord2\3c{BLACK}\1c{WHITE}\shad2\4a&H80&"
        rf"\fad(150,0){clicks}\p1}}{CURSOR}")
    bx, by = BELL_X + 6, BELL_Y + 8
    add(20, s + T_TO_BELL / 1000, c_end,
        rf"{{\an7\move({cx},{cy},{bx},{by},0,{T_CLICK2 - T_TO_BELL - 120})\bord2\3c{BLACK}\1c{WHITE}\shad2\4a&H80&"
        rf"\fad(0,200)\t({T_CLICK2 - T_TO_BELL - 60},{T_CLICK2 - T_TO_BELL + 60},\fscx82\fscy82)"
        rf"\t({T_CLICK2 - T_TO_BELL + 60},{T_CLICK2 - T_TO_BELL + 160},\fscx100\fscy100)\p1}}{CURSOR}")
    return lines


SUBSCRIBE_WORDS = ("subscribe", "obuna")  # English and Uzbek ("obuna bo'ling")
LIKE_WORD = re.compile(r"\b(like|layk)\b")


def subscribe_at(text: str) -> int:
    """Character index of the first subscribe word in the narration, -1 when there is none."""
    low = text.lower()
    found = [low.find(w) for w in SUBSCRIBE_WORDS if low.find(w) >= 0]
    return min(found) if found else -1


def spoken_start(text: str, duration: float) -> float:
    """Where in a scene the narrator says "subscribe" (estimated from its place in the sentence), minus a beat
    so the button pops in just as the word is heard."""
    at = subscribe_at(text)
    if at < 0:
        return LEAD
    return max(LEAD, round(duration * at / max(1, len(text)) - 0.3, 3))


def plan(durations: list[float], beats: list[str], texts: list[str] | None = None) -> dict[int, float]:
    """{scene index: CTA start inside that scene}. Exactly one CTA per video (the last scene is only a fallback).
    With `texts` (the narrations) the animation lands on the scene where the narrator says "subscribe"."""
    if not enabled() or not durations:
        return {}
    out: dict[int, float] = {}
    last = len(durations) - 1
    if texts:  # the script's own subscribe line wins over the timer
        for i, (d, text) in enumerate(zip(durations, texts)):
            if i < last and subscribe_at(text) >= 0 and d >= MIN_SCENE and (not beats or beats[i] != "hook"):
                out[i] = round(min(spoken_start(text, d), d - DURATION - 0.2), 3)
                break
    if not out:
        at = float(getattr(settings, "SUBSCRIBE_CTA_AT_SEC", 40))
        t = 0.0
        for i, (d, beat) in enumerate(zip(durations, beats)):
            if t >= at and beat not in ("hook", "punchline") and d >= MIN_SCENE and i < last:
                out[i] = LEAD
                break
            t += d
    # once per video: the last scene only gets it when no mid-video scene could hold it
    if getattr(settings, "SUBSCRIBE_CTA_END", True) and not out and sum(durations) >= 30:
        from .render import FADE_OUT_SEC

        room = durations[last] - FADE_OUT_SEC - DURATION
        if room >= 0.1:  # must finish before the fade to black
            want = spoken_start(texts[last], durations[last]) if texts and subscribe_at(texts[last]) >= 0 \
                else max(LEAD, durations[last] / 3)
            out[last] = round(min(room, want), 3)
    return out


# ------------------------------------------------------------------ LIKE button
LIKE_X, LIKE_Y, LIKE_W, LIKE_H = 1130, 120, 270, 100
THUMB = ("m 0 26 l 14 26 l 14 62 l 0 62 m 19 28 b 26 21 31 9 34 0 b 42 0 46 9 42 22 l 60 22 b 66 22 68 28 66 33 "
         "l 61 56 b 59 62 55 62 51 62 l 19 62")


def like_events(start: float) -> list[str]:
    """ASS lines of a LIKE button: pops in, a thumb presses it, it turns blue "LIKED"."""
    end = start + 3.2
    click = start + 1.0
    pop = r"\fscx60\fscy60\t(0,180,\fscx108\fscy108)\t(180,260,\fscx100\fscy100)"
    shadow = r"\shad4\4a&H80&\4c&H000000&"
    lines = []

    def add(layer: int, t0: float, t1: float, text: str) -> None:
        lines.append(f"Dialogue: {layer},{ass_time(t0)},{ass_time(t1)},Default,,0,0,0,,{text}\n")

    rect = rounded_rect(LIKE_W, LIKE_H, 22)
    add(10, start, click, rf"{{\an5\pos({LIKE_X},{LIKE_Y})\bord0{shadow}\1c&H4A4A4A&\fad(120,0){pop}\p1}}{rect}")
    add(10, click, end, rf"{{\an5\pos({LIKE_X},{LIKE_Y})\bord0{shadow}\1c&HD45F06&\fad(0,300)\fscx92\fscy92\t(0,140,\fscx100\fscy100)\p1}}{rect}")
    add(11, start, click, rf"{{\an4\pos({LIKE_X - 30},{LIKE_Y})\fnArial\b1\fs50\bord0\shad0\1c&HFFFFFF&\fsp2\fad(120,0){pop}}}LIKE")
    add(11, click, end, rf"{{\an4\pos({LIKE_X - 40},{LIKE_Y})\fnArial\b1\fs46\bord0\shad0\1c&HFFFFFF&\fsp1\fad(0,300)}}LIKED")
    swing = r"\t(0,120,\fscx115\fscy115\frz-12)\t(120,260,\fscx100\fscy100\frz0)"
    add(12, start, end, rf"{{\an5\pos({LIKE_X - 78},{LIKE_Y - 4})\bord3\3c&H000000&\1c&HFFFFFF&\fad(120,300){pop}\p1}}{THUMB}")
    add(13, click, click + 0.7, rf"{{\an5\pos({LIKE_X - 78},{LIKE_Y - 4})\bord0\1c&HFFFFFF&\fad(0,500)\fscx100\fscy100{swing}\p1}}{THUMB}")
    return lines


LIKE_DURATION = 3.2
LIKE_AFTER_SUBSCRIBE = 2.4  # the like button starts this long after the subscribe one
LIKE_SOUNDS = [CtaSound("pop", 0.0, 0.5), CtaSound("click", 1.0, 0.7)]


def plan_likes(durations: list[float], texts: list[str], sub_plan: dict[int, float]) -> dict[int, float]:
    """{scene index: LIKE start inside that scene}: right after the subscribe animation, and in the last scene
    at the narrator's "like"."""
    if not enabled() or not durations:
        return {}
    out: dict[int, float] = {}
    last = len(durations) - 1
    for i, start in sorted(sub_plan.items()):
        if i == last:
            continue  # the closing scene gets its own like below
        at = start + LIKE_AFTER_SUBSCRIBE
        if at + LIKE_DURATION <= durations[i] - 0.1:
            out[i] = round(at, 3)
        elif i + 1 < last and durations[i + 1] >= LIKE_DURATION + LEAD + 0.2:
            out[i + 1] = LEAD
        break  # one pair per video
    if getattr(settings, "SUBSCRIBE_CTA_END", True) and last not in out and sum(durations) >= 30:
        text = texts[last].lower() if texts else ""
        word = LIKE_WORD.search(text)
        if word:
            from .render import FADE_OUT_SEC

            room = durations[last] - FADE_OUT_SEC - LIKE_DURATION
            if room >= 0.1:
                est = max(LEAD, durations[last] * word.start() / max(1, len(text)) - 0.3)
                out[last] = round(min(room, est), 3)
    return out
