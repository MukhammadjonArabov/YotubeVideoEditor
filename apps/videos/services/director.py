"""The "Rejissyor" (director) step: after the script is written, Gemini reads the whole script and
marks every scene with emotion / intensity / pace / pause / camera move / transition / SFX /
music cue / on-screen text. The model's answer is then checked in code, so the rules hold even
when the model bends them:

* never more than 3 scenes in a row with the same emotion;
* SFX on about 1 scene in 3-4, never the same SFX twice in a row;
* a "pattern interrupt" (SFX, on-screen text, music cue, punch/shake, a non-cut transition)
  at least every PATTERN_GAP_SEC seconds;
* music cues: stinger only on punchlines, change_mood at most twice, about one cue per 5 scenes;
* camera: few motionless scenes, never the same move twice in a row;
* sensible values only (known choices, intensity 1-3, offsets inside the scene...).
"""
from __future__ import annotations

import logging
from typing import Optional

from django.conf import settings
from pydantic import BaseModel, Field

from . import gemini_client

logger = logging.getLogger(__name__)

WORDS_PER_SEC = 2.5  # used to estimate scene length before the voice exists
MAX_SAME_EMOTION = 3
SFX_EVERY = 3.5  # about one SFX scene per 3-4 scenes
PATTERN_GAP_SEC = 35  # longest stretch without a pattern interrupt
BATCH = 40  # scenes per Gemini call (long videos are sent in parts)
MAX_SFX_PER_SCENE = 2
MUSIC_CUE_EVERY = 5  # at most one music cue per ~5 scenes
MAX_MOOD_CHANGES = 2
TEXT_EVERY = 6  # at most one on-screen text per ~6 scenes
STILL_EVERY = 6  # at most one motionless ("none") scene per 6 scenes
# Which music cues survive the cap first.
MUSIC_PRIORITY = {"drop_out": 0, "change_mood": 1, "swell": 2, "stinger": 3}
# Emotion used to break a run that got too long (keeps the mood family).
EMOTION_BREAK = {"neutral": "curious", "curious": "neutral", "excited": "curious", "happy": "neutral",
                 "funny": "neutral", "scared": "tense", "tense": "serious", "sad": "serious", "awe": "curious",
                 "whisper": "tense", "serious": "curious"}
SFX_ALTERNATIVE = {"whoosh": "swoosh", "swoosh": "whoosh", "pop": "click", "click": "pop", "ding": "pop",
                   "boing": "pop", "impact": "riser", "riser": "impact"}


# ------------------------------------------------------------------ schema
class SfxOut(BaseModel):
    tag: str
    offset_ms: int = 0
    gain_db: float = -8.0


class SceneDirection(BaseModel):
    index: int = Field(description="Scene number as given")
    emotion: str
    intensity: int = Field(description="1-3")
    pace: str = Field(description="slow | normal | fast")
    pause_after_ms: int = Field(default=0, description="0-1500, dramatic pause after the line")
    camera_move: str
    transition_in: str
    sfx: list[SfxOut] = Field(default_factory=list)
    music_cue: str = "continue"
    on_screen_text: Optional[str] = Field(default=None, description="1-4 words in CAPS, or null")


class DirectionOut(BaseModel):
    scenes: list[SceneDirection]


# ------------------------------------------------------------------ choices
def choices() -> dict[str, list[str]]:
    from ..models import Scene

    return {
        "emotion": list(Scene.Emotion.values),
        "pace": list(Scene.Pace.values),
        "camera_move": list(Scene.CameraMove.values),
        "transition_in": list(Scene.Transition.values),
        "music_cue": list(Scene.MusicCue.values),
        "sfx": list(settings.SFX_TAGS),
    }


def estimate_seconds(narration: str) -> float:
    return max(1.5, len(narration.split()) / WORDS_PER_SEC) + 0.4


# ------------------------------------------------------------------ prompt
def build_prompt(project, scenes: list, start: int, context: list[dict]) -> str:
    c = choices()
    lines = []
    t = sum(estimate_seconds(s.narration) for s in scenes[:start])
    for i, s in enumerate(scenes[start:start + BATCH], start=start + 1):
        lines.append(f"{i}. [{s.beat_type}, ~{t:.0f}s] {s.narration}")
        t += estimate_seconds(s.narration)
    ctx = ""
    if context:
        ctx = "Directions you already gave to the scenes right before this part (keep variety with them):\n" + \
              "\n".join(f"{d['index']}: {d['emotion']}, sfx={[x['tag'] for x in d['sfx']]}" for d in context) + "\n\n"
    return f"""You are the director and sound designer of a faceless, hand-drawn animated YouTube explainer
(channel: funny, curious videos about ancient humans; US audience; English narration).
Video topic: {project.topic}. Music mood: {(project.script_json or {}).get('mood', 'mysterious')}.

For EVERY scene below, decide how it is voiced and edited. Allowed values:
- emotion: {", ".join(c['emotion'])}; intensity 1-3
- pace: {", ".join(c['pace'])}; pause_after_ms: 0-1500 (only for dramatic beats, reveals, jokes)
- camera_move: {", ".join(c['camera_move'])}
- transition_in (how this scene starts): {", ".join(c['transition_in'])}
- sfx: list of {{tag, offset_ms (from scene start), gain_db (-14..-4)}}; tags: {", ".join(c['sfx'])}
- music_cue: {", ".join(c['music_cue'])}
- on_screen_text: 1-4 big words in CAPS (a number, date or key word), or null

RULES
- Emotion must fit the meaning: scary -> scared/tense with slow pace; funny -> funny with sfx boing or pop;
  amazing fact -> awe; a secret being revealed -> whisper, then excited in the next scene.
- Never more than 3 scenes in a row with the same emotion.
- Every 20-40 seconds a small pattern interrupt: a camera change (punch_zoom / shake), an sfx,
  an on_screen_text or a music_cue.
- SFX only where it means something (punchline, joke, transition): about one scene in 3-4. Never the same sfx in
  two scenes in a row. An sfx at a punchline sits on the key word (estimate offset_ms from the words before it).
- transition_in is "cut" by default; crossfade / whip / dip_to_black / flash only when a section or idea changes.
  flash = punchline hit; dip_to_black = big section change or dark turn.
- shake only for a scary hit; punch_zoom for surprises and hook beats. camera_move "none" very rarely
  (a still picture looks dead); never the same camera_move in two scenes in a row.
- on_screen_text rarely (1 in 6-8 scenes), only for numbers, dates, names or one key idea.
- music_cue "continue" in at least 4 of 5 scenes; drop_out right before a big reveal; swell on an epic moment;
  stinger only on a punchline; change_mood at most twice per video, only when the story's mood really turns.

{ctx}SCENES (number. [beat, ~start time] narration):
{chr(10).join(lines)}

Return JSON: {{"scenes": [ ... one object per scene, with "index" = the scene number ... ]}}"""


# ------------------------------------------------------------------ rule enforcement (unit-tested)
def _clean(d: dict, n_words: int) -> dict:
    c = choices()
    out = dict(d)
    out["emotion"] = d.get("emotion") if d.get("emotion") in c["emotion"] else "neutral"
    out["intensity"] = min(3, max(1, int(d.get("intensity") or 2)))
    out["pace"] = d.get("pace") if d.get("pace") in c["pace"] else "normal"
    out["pause_after_ms"] = min(1500, max(0, int(d.get("pause_after_ms") or 0))) // 50 * 50
    out["camera_move"] = d.get("camera_move") if d.get("camera_move") in c["camera_move"] else ""
    out["transition_in"] = d.get("transition_in") if d.get("transition_in") in c["transition_in"] else "cut"
    out["music_cue"] = d.get("music_cue") if d.get("music_cue") in c["music_cue"] else "continue"
    text = " ".join(str(d.get("on_screen_text") or "").split()).upper()
    out["on_screen_text"] = " ".join(text.split()[:4])[:40]
    max_ms = int(estimate_seconds(" ".join(["w"] * n_words)) * 1000) - 300
    sfx = []
    for x in d.get("sfx") or []:
        x = x if isinstance(x, dict) else x.model_dump()
        tag = str(x.get("tag", "")).lower().strip()
        if tag in c["sfx"] and tag not in [s["tag"] for s in sfx]:
            sfx.append({"tag": tag, "offset_ms": min(max(0, int(x.get("offset_ms") or 0)), max(0, max_ms)),
                        "gain_db": round(min(-2.0, max(-20.0, float(x.get("gain_db", settings.SFX_GAIN_DB)))), 1)})
    out["sfx"] = sfx[:MAX_SFX_PER_SCENE]
    return out


def _is_interrupt(d: dict) -> bool:
    return bool(d["sfx"] or d["on_screen_text"] or d["music_cue"] != "continue"
                or d["camera_move"] in ("punch_zoom", "shake") or d["transition_in"] not in ("cut", ""))


def enforce_rules(directions: list[dict], scenes: list) -> list[dict]:
    """Clean every direction, then apply the variety rules. `directions[i]` belongs to `scenes[i]`."""
    dirs = [_clean(d, len(s.narration.split())) for d, s in zip(directions, scenes)]
    n = len(dirs)
    if not n:
        return dirs
    dirs[0]["transition_in"] = "cut"  # nothing to transition from

    # 1) emotion runs: the 4th scene in a row with the same emotion gets a neighbouring one
    run = 1
    for i in range(1, n):
        if dirs[i]["emotion"] == dirs[i - 1]["emotion"]:
            run += 1
            if run > MAX_SAME_EMOTION:
                dirs[i]["emotion"] = EMOTION_BREAK.get(dirs[i]["emotion"], "neutral")
                run = 1
        else:
            run = 1

    # 2) same SFX twice in a row -> its alternative (or dropped)
    prev_tags: set[str] = set()
    for d in dirs:
        tags = []
        for x in d["sfx"]:
            if x["tag"] in prev_tags:
                alt = SFX_ALTERNATIVE.get(x["tag"])
                if not alt or alt in prev_tags or alt in tags:
                    continue
                x = {**x, "tag": alt}
            tags.append(x["tag"])
            x_list = d.setdefault("_sfx", [])
            x_list.append(x)
        d["sfx"] = d.pop("_sfx", [])
        prev_tags = set(tags)

    # 3) SFX density: keep at most ~n/3.5 scenes with SFX; punchlines and hooks keep theirs first
    limit = max(1, round(n / SFX_EVERY))
    with_sfx = [i for i, d in enumerate(dirs) if d["sfx"]]
    if len(with_sfx) > limit:
        rank = {"punchline": 0, "hook": 1, "build": 2, "normal": 3}
        keep = set(sorted(with_sfx, key=lambda i: (rank.get(scenes[i].beat_type, 3), i))[:limit])
        for i in with_sfx:
            if i not in keep:
                dirs[i]["sfx"] = []

    # 4) music cues: stinger only on punchlines, few mood changes, one cue per ~MUSIC_CUE_EVERY scenes
    moods = 0
    for i, d in enumerate(dirs):
        cue = d["music_cue"]
        if cue == "stinger" and scenes[i].beat_type != "punchline":
            d["music_cue"] = "continue"
        elif cue == "change_mood":
            moods += 1
            if moods > MAX_MOOD_CHANGES:
                d["music_cue"] = "continue"
    cued = [i for i, d in enumerate(dirs) if d["music_cue"] != "continue"]
    limit = max(1, round(n / MUSIC_CUE_EVERY))
    if len(cued) > limit:
        keep = set(sorted(cued, key=lambda i: (MUSIC_PRIORITY.get(dirs[i]["music_cue"], 9), i))[:limit])
        for i in cued:
            if i not in keep:
                dirs[i]["music_cue"] = "continue"

    # 5) camera: no repeats in a row (-> automatic), few motionless scenes
    stills = 0
    for i, d in enumerate(dirs):
        if i and d["camera_move"] and d["camera_move"] == dirs[i - 1]["camera_move"]:
            d["camera_move"] = ""
        if d["camera_move"] == "none":
            stills += 1
            if stills > max(1, n // STILL_EVERY):
                d["camera_move"] = ""

    # 6) on-screen text: rare, so it stays special (punchlines and hooks keep theirs first)
    texts = [i for i, d in enumerate(dirs) if d["on_screen_text"]]
    limit = max(1, round(n / TEXT_EVERY))
    if len(texts) > limit:
        rank = {"punchline": 0, "hook": 1, "build": 2, "normal": 3}
        keep = set(sorted(texts, key=lambda i: (rank.get(scenes[i].beat_type, 3), i))[:limit])
        for i in texts:
            if i not in keep:
                dirs[i]["on_screen_text"] = ""

    # 7) pattern interrupt at least every PATTERN_GAP_SEC: add a whip into the scene that ends the gap
    t = since = 0.0
    for i, (d, s) in enumerate(zip(dirs, scenes)):
        if _is_interrupt(d):
            since = 0.0
        elif since >= PATTERN_GAP_SEC and i > 0:
            d["transition_in"] = "whip"
            since = 0.0
        dur = estimate_seconds(s.narration)
        since += dur
        t += dur
    return dirs


# ------------------------------------------------------------------ main
def direct(project) -> list[dict]:
    """Ask Gemini for directions (in batches for long videos) and return them rule-checked."""
    from concurrent.futures import ThreadPoolExecutor

    scenes = list(project.scenes.order_by("order"))
    prompts = [build_prompt(project, scenes, start, []) for start in range(0, len(scenes), BATCH)]
    # Parts are sent at the same time (a 70-scene video: ~2 min instead of ~4); variety across the
    # part boundaries is guaranteed by enforce_rules below.
    with ThreadPoolExecutor(max_workers=min(4, len(prompts))) as pool:
        results = list(pool.map(lambda pr: gemini_client.generate_json(pr, DirectionOut, temperature=0.6), prompts))
    raw: dict[int, dict] = {}
    for out in results:
        for d in out.scenes:
            raw[d.index] = d.model_dump()
    directions = [raw.get(i, {}) for i in range(1, len(scenes) + 1)]
    missing = sum(1 for d in directions if not d)
    if missing == len(scenes):
        raise gemini_client.GeminiError("Rejissyor hech bir sahnaga javob bermadi.")
    if missing:
        logger.warning("Director skipped %s scenes of project %s - defaults used", missing, project.pk)
    return enforce_rules(directions, scenes)


VOICE_FIELDS = {"emotion", "intensity", "pace"}
AUTHOR_FIELDS = VOICE_FIELDS | {"pause_after_ms"}  # kept as the script author wrote them
FIELDS = ["emotion", "intensity", "pace", "pause_after_ms", "camera_move", "transition_in", "sfx", "music_cue",
          "on_screen_text"]


def apply(project, directions: list[dict]) -> int:
    """Write directions onto the scenes; clips of changed scenes are re-rendered. Returns changed count."""
    from ..models import Project

    changed = 0
    authored = [bool(x.get("emotion")) for x in (project.script_json or {}).get("scenes", [])]
    for i, (scene, d) in enumerate(zip(project.scenes.order_by("order"), directions)):
        pinned = i < len(authored) and authored[i]  # the script author already voiced this scene
        updates = {f: d[f] for f in FIELDS if f in d and getattr(scene, f) != d[f]
                   and not (pinned and f in AUTHOR_FIELDS)}
        if not updates:
            continue
        for f, v in updates.items():
            setattr(scene, f, v)
        scene.clip_hash = ""
        fields = [*updates, "clip_hash"]
        if scene.audio and VOICE_FIELDS & set(updates):  # new delivery -> voice is made again next time
            scene.audio.delete(save=False)
            scene.audio, scene.audio_duration, scene.subtitle_words = "", None, None
            fields += ["audio", "audio_duration", "subtitle_words"]
        scene.save(update_fields=fields)
        changed += 1
    if changed:
        Project.objects.filter(pk=project.pk).update(has_unrendered_changes=True)
    return changed


def summary(project) -> dict:
    """Small stats for the UI: emotion share, SFX count, on-screen texts."""
    from collections import Counter

    scenes = list(project.scenes.all())
    if not scenes:
        return {}
    emotions = Counter(s.emotion for s in scenes)
    return {
        "emotions": [(e, round(c * 100 / len(scenes))) for e, c in emotions.most_common()],
        "sfx": sum(len(s.sfx or []) for s in scenes),
        "texts": sum(1 for s in scenes if s.on_screen_text),
        "directed": any(s.emotion != "neutral" or s.sfx or s.camera_move for s in scenes),
    }
