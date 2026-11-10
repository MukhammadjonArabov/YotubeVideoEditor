"""ASS subtitles (prompt 5.5): 3-6 words per caption, timed from word boundaries or
proportionally from sentence length; hook scenes get a bigger pop-in style.
With real word timings the word being spoken is highlighted (karaoke-style captions)."""
from __future__ import annotations

import re

MIN_WORDS, MAX_WORDS = 3, 6
# Colour of the word being spoken (ASS &HBBGGRR): yellow on white captions, white on yellow hook captions.
HIGHLIGHT = {"Default": "&H0000E5FF&", "Hook": "&H00FFFFFF&"}
BASE_COLOUR = {"Default": "&H00FFFFFF&", "Hook": "&H0000E5FF&"}

ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,66,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,5,2,2,120,120,70,1
Style: Hook,Arial,86,&H0000E5FF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,3,2,100,100,90,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def ass_time(t: float) -> str:
    t = max(0.0, t)
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def ass_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "(").replace("}", ")").replace("\n", " ")


def group_words(words: list[str]) -> list[list[int]]:
    """Indices of words per caption: up to MAX_WORDS, breaking early after punctuation once MIN_WORDS reached."""
    groups: list[list[int]] = []
    cur: list[int] = []
    for i, w in enumerate(words):
        cur.append(i)
        if len(cur) >= MAX_WORDS or (len(cur) >= MIN_WORDS and re.search(r"[.,!?;:…]$", w)):
            groups.append(cur)
            cur = []
    if cur:
        if groups and len(cur) < MIN_WORDS and len(groups[-1]) + len(cur) <= MAX_WORDS + 2:
            groups[-1].extend(cur)
        else:
            groups.append(cur)
    return groups


def proportional_timings(text: str, duration: float) -> list[dict]:
    """No word boundaries (e.g. Gemini TTS): spread words over the audio by character length."""
    words = text.split()
    if not words or duration <= 0:
        return []
    weights = [len(w) + 2 for w in words]
    total = sum(weights)
    t = 0.0
    out = []
    for w, wt in zip(words, weights):
        d = duration * wt / total
        out.append({"word": w, "start": round(t, 3), "end": round(t + d, 3)})
        t += d
    return out


def caption_events(scene_text: str, duration: float, word_timings: list[dict] | None) -> list[tuple[float, float, str]]:
    """(start, end, text) captions for one scene, times relative to the scene start."""
    timed = word_timings or proportional_timings(scene_text, duration)
    if not timed:
        return []
    words = [w["word"] for w in timed]
    events = []
    groups = group_words(words)
    for gi, g in enumerate(groups):
        start = timed[g[0]]["start"]
        end = timed[groups[gi + 1][0]]["start"] if gi + 1 < len(groups) else max(timed[g[-1]]["end"], duration)
        events.append((round(start, 3), round(max(end, start + 0.3), 3), " ".join(words[i] for i in g)))
    return events


def word_events(duration: float, word_timings: list[dict]) -> list[tuple[float, float, list[str], int, bool]]:
    """Karaoke events: (start, end, words of the caption, index of the spoken word, first-of-caption)."""
    words = [w["word"] for w in word_timings]
    groups = group_words(words)
    out = []
    for gi, g in enumerate(groups):
        group_end = word_timings[groups[gi + 1][0]]["start"] if gi + 1 < len(groups) else max(word_timings[g[-1]]["end"], duration)
        for j, wi in enumerate(g):
            start = word_timings[g[0]]["start"] if j == 0 else word_timings[wi]["start"]
            end = word_timings[g[j + 1]]["start"] if j + 1 < len(g) else group_end
            if end - start < 0.02:
                continue
            out.append((round(start, 3), round(end, 3), [words[i] for i in g], j, j == 0))
    return out


def scene_ass(scene_text: str, duration: float, word_timings: list[dict] | None, hook: bool = False,
              karaoke: bool = True) -> str:
    lines = [ASS_HEADER]
    style = "Hook" if hook else "Default"
    if karaoke and word_timings:
        pop = r"{\fad(80,0)\fscx70\fscy70\t(0,120,\fscx100\fscy100)}" if hook else r"{\fad(60,0)}"
        hi, base = HIGHLIGHT[style], BASE_COLOUR[style]
        for start, end, words, spoken, first in word_events(duration, word_timings):
            text = " ".join("{\\1c" + hi + "}" + ass_escape(w) + "{\\1c" + base + "}" if k == spoken else ass_escape(w)
                            for k, w in enumerate(words))
            lines.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},{style},,0,0,0,,{pop if first else ''}{text}\n")
        return "".join(lines)
    pop = r"{\fad(80,60)\fscx70\fscy70\t(0,120,\fscx100\fscy100)}" if hook else r"{\fad(60,40)}"
    for start, end, text in caption_events(scene_text, duration, word_timings):
        lines.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},{style},,0,0,0,,{pop}{ass_escape(text)}\n")
    return "".join(lines)


def srt_time(t: float) -> str:
    ms = int(round(max(0.0, t) * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def srt_for_scenes(items: list[tuple[float, str, float, list[dict] | None]]) -> str:
    """A whole-video .srt (for uploading to YouTube) from (scene start, narration, voice length, word timings)."""
    blocks = []
    for offset, text, duration, words in items:
        for start, end, caption in caption_events(text, duration, words):
            blocks.append(f"{len(blocks) + 1}\n{srt_time(offset + start)} --> {srt_time(offset + end)}\n{caption}\n")
    return "\n".join(blocks)
