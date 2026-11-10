"""Script generation with Gemini (prompt 5.2): strict JSON -> Project + Scenes."""
from __future__ import annotations

import logging
import math
from typing import Optional

from django.conf import settings
from django.db import transaction
from pydantic import BaseModel, Field

from . import gemini_client

logger = logging.getLogger(__name__)

BEATS = {"hook", "build", "punchline", "normal"}


# ------------------------------------------------------------------ schema
class SceneOut(BaseModel):
    narration: str = Field(description="What the narrator says in this scene (English)")
    image_prompt: str = Field(description="Visual content of the scene only - no style words, no text in image")
    beat_type: str = Field(description="hook | build | punchline | normal")
    sfx_cue: Optional[str] = Field(default=None, description="Optional sound-effect tag from the allowed list, else null")
    fact_source: Optional[str] = Field(default=None, description="Source of the fact stated in this scene, or null")
    scene_kind: str = Field(default="hero", description="hero (the main character acts) | fact (no main character: "
                                                        "evidence, event, object, place, other people)")
    # Voice direction written by the script author (Claude); when set, the Gemini director leaves it alone.
    emotion: Optional[str] = Field(default=None, description="neutral|curious|excited|happy|funny|scared|tense|sad|awe|whisper|serious")
    intensity: Optional[int] = Field(default=None, description="1-3")
    pace: Optional[str] = Field(default=None, description="slow | normal | fast")
    pause_after_ms: Optional[int] = Field(default=None, description="0-1500 dramatic pause after the line")


class ScriptOut(BaseModel):
    title: str
    title_alternatives: list[str]
    description: str
    tags: list[str]
    mood: str
    sources: list[str] = Field(default_factory=list, description="Real, well-known publications a fact-checker could look up")
    scenes: list[SceneOut]


# ------------------------------------------------------------------ math (unit-tested)
def scene_count(target_duration_sec: int, seconds_per_image: int) -> int:
    """Number of scenes = target duration / seconds per image (at least 3)."""
    return max(3, round(target_duration_sec / max(1, seconds_per_image)))


def word_budget(target_duration_sec: int, words_per_minute: int | None = None) -> int:
    wpm = words_per_minute or settings.WORDS_PER_MINUTE
    return round(target_duration_sec / 60 * wpm)


def words_per_scene(target_duration_sec: int, seconds_per_image: int) -> int:
    return max(6, math.floor(word_budget(target_duration_sec) / scene_count(target_duration_sec, seconds_per_image)))


def count_ok(got: int, wanted: int, tolerance: float = 0.2) -> bool:
    return abs(got - wanted) <= max(2, wanted * tolerance)


HOOK_SECONDS = 35  # the hook covers the first ~30-40 s
HOOK_SCENE_SEC = 3.0  # hook scenes are one short sentence each, so the picture changes every 2-3 s
HOOK_MAX_SEC = 40
HOOK_MAX_WORDS = 10  # per hook scene
SPEECH_WORDS_PER_SEC = 2.5
MAX_SAME_KIND_RATIO = 0.15  # share of hero->hero / fact->fact neighbours tolerated before asking again


def hook_scene_target() -> int:
    """How many short scenes the 30-40 s hook is written as (~12)."""
    return round(HOOK_SECONDS / HOOK_SCENE_SEC)


def expected_scene_count(target_duration_sec: int, seconds_per_image: int) -> int:
    """Short hook scenes + normal scenes for the rest of the video."""
    body = max(1, round((target_duration_sec - HOOK_SECONDS) / max(1, seconds_per_image)))
    return max(3, hook_scene_target() + body)


def spoken_seconds(text: str, words_per_sec: float = SPEECH_WORDS_PER_SEC) -> float:
    return len(text.split()) / words_per_sec + 0.15


def hook_scene_count_for(scenes, words_per_sec: float = SPEECH_WORDS_PER_SEC) -> int:
    """The hook = the opening scenes that fit in the first ~40 seconds (at least 3). When the script already
    marks its opening scenes as "hook" and they fit (the estimate is conservative: +8 s slack), those marks win."""
    marked = 0
    for s in scenes:
        if (getattr(s, "beat_type", "") or "").strip().lower() != "hook":
            break
        marked += 1
    if marked >= 3 and sum(spoken_seconds(s.narration, words_per_sec) for s in scenes[:marked]) <= HOOK_MAX_SEC + 8:
        return marked
    t, n = 0.0, 0
    for s in scenes:
        t += spoken_seconds(s.narration, words_per_sec)
        if t > HOOK_MAX_SEC:
            break
        n += 1
    return min(len(scenes), max(3, n))


def same_kind_pairs(scenes) -> int:
    """Neighbours with the same kind (hero/hero or fact/fact) - 0 means a perfect alternation."""
    kinds = [s.scene_kind for s in scenes]
    return sum(1 for a, b in zip(kinds, kinds[1:]) if a == b)


def alternation_ok(scenes) -> bool:
    return same_kind_pairs(scenes) <= max(1, int(len(scenes) * MAX_SAME_KIND_RATIO))


# ------------------------------------------------------------------ cleaning (unit-tested)
def clean_script(data: ScriptOut, default_mood: str, hook_scenes: int = 2, realistic: bool = False) -> ScriptOut:
    """Enforce the rules the model sometimes bends: the first `hook_scenes` scenes are the hook (and only
    they), allowed sfx tags, allowed mood, 5 title alternatives, non-empty narration, and fact scenes
    never ask the image model for the main character."""
    from .images import MAIN_CHARACTER_WORDS

    allowed_sfx = set(settings.SFX_TAGS)
    scenes = [s for s in data.scenes if s.narration.strip()]
    for i, s in enumerate(scenes):
        beat = (s.beat_type or "normal").strip().lower()
        if beat not in BEATS:
            beat = "normal"
        if i < hook_scenes:
            beat = "hook"
        elif beat == "hook":
            beat = "build"
        s.beat_type = beat
        kind = (s.scene_kind or "").strip().lower()
        if realistic:  # photo-like niches have no main character: every scene explains, "fact" scenes carry a source
            kind = "fact" if kind == "fact" else "explain"
        elif kind not in ("hero", "fact"):
            kind = "hero" if MAIN_CHARACTER_WORDS.search(s.image_prompt or "") else "fact"
        s.scene_kind = kind
        cue = (s.sfx_cue or "").strip().lower()
        s.sfx_cue = cue if cue in allowed_sfx else None
        s.narration = s.narration.strip()
        s.image_prompt = s.image_prompt.strip()
        if kind == "fact":  # a fact scene must not pull the hero's character sheet into the image
            s.image_prompt = MAIN_CHARACTER_WORDS.sub("an ancient person", s.image_prompt)
    data.scenes = scenes
    mood = (data.mood or "").strip().lower()
    data.mood = mood if mood in settings.MUSIC_MOODS else default_mood
    alts = [t.strip() for t in data.title_alternatives if t.strip() and t.strip() != data.title.strip()]
    data.title_alternatives = alts[:5]
    data.tags = [t.strip() for t in data.tags if t.strip()][:15]
    return data


# ------------------------------------------------------------------ prompt
def build_prompt(project, n_scenes: int, words: int) -> str:
    niche = project.niche
    brief = niche.prompt_brief() if niche else ""
    character = niche.character_description if niche and niche.character_description else "a friendly stick-figure narrator character"
    past = list(project.__class__.objects.exclude(pk=project.pk).values_list("topic", flat=True)[:100])
    hook = hook_scene_target()
    hook_words = round(HOOK_SECONDS * SPEECH_WORDS_PER_SEC)
    per = max(6, (words - hook_words) // max(1, n_scenes - hook))
    return f"""You write scripts for a faceless, animated stick-figure YouTube explainer channel (English narration).
{brief}

VIDEO TOPIC: {project.topic}
TARGET: {project.target_duration_sec // 60} min {project.target_duration_sec % 60} s  ->  about {words} spoken words in total.
SCENES: exactly {n_scenes} scenes, one image each. Scenes 1-{hook} are the hook (below); every later scene has
about {per} words of narration (~{project.seconds_per_image} s on screen).

THE HOOK = scenes 1-{hook}, the first ~30-40 seconds. It decides whether people keep watching, so spend the most
care here. Write it as {hook} very short scenes: ONE sentence each, 5-9 words (2-3 seconds), each with its own
picture, so the images change fast. Together they must answer, in this order:
  1. Grab: drop straight into the topic with a startling fact, a number, a scene already in motion or a sharp
     question. Never a greeting, the channel name or "in this video".
  2. Why watch: why this matters to the viewer personally, right now (a concrete link to their own life).
  3. What they get: a clear, specific promise of what they will know or understand by the end of the video.
  4. Open loop: one intriguing question that is answered only later in the video.
All hook scenes have beat_type "hook". After the hook, keep the promise: the body answers the open loop before the end.

TWO KINDS OF SCENES - ALTERNATE THEM: hero, fact, hero, fact, ... (scene_kind)
- "hero": the recurring main character acts out the idea (a little story moment, emotion, mild humour).
  The main character is: {character}. Refer to him as "the main character" in the image prompt.
- "fact": NO main character. Show the evidence or the event itself: a real finding, an artefact, a fossil or skull,
  cave art, an animal, a landscape, a migration map shape, a timeline, a group of other ancient people, a simple diagram
  (no letters or numbers in the image). The narration states a concrete, accurate fact, date, number or research finding.
  Never write "the main character" in a fact scene's image prompt.
- Every scene, hero or fact, must serve THIS topic directly. No side stories, no general history lessons that drift
  away from the video topic.

STYLE
- Conversational, simple sentences, mild humour, no filler, no "in this video we will".
- Factual and accurate. Anything uncertain is said as uncertain ("researchers think", "evidence suggests"). No invented statistics.
- ORIGINALITY (required): include at least one clear personal-take line from the narrator and at least one modern-life comparison; end with a short thoughtful payoff, not a generic "subscribe".
- Advertiser-friendly: violence, drugs and sex only brief and non-graphic.
- Mark clear twist / reveal / joke moments as "punchline"; rising-tension scenes as "build"; others "normal".
- sfx_cue: only when a scene clearly benefits (a reveal, a joke, a scene change). Allowed: {", ".join(settings.SFX_TAGS)}. Otherwise null. Use them sparingly (about 1 in 5 scenes).

IMAGE PROMPTS
- Describe ONLY what is visible in the scene (characters, action, place, props, expression). No art-style words (the app adds the style), no text or letters in the image.
- Keep each prompt under 40 words, concrete and drawable.

METADATA
- title: curiosity question, under 60 characters; the hook must deliver on its promise. title_alternatives: 5 different options.
- description: 2 short paragraphs + a line "Sources:" (leave the actual list to the sources field).
- tags: 8-12 search tags. mood: one of {", ".join(settings.MUSIC_MOODS)}.
- sources: 2-4 REAL, well-known books/papers/institutions a fact-checker could look up. If unsure, give fewer.

Do not repeat these topics I already made: {"; ".join(past) or "none"}.
Return JSON only."""


# ------------------------------------------------------------------ main
def generate(project) -> ScriptOut:
    n = expected_scene_count(project.target_duration_sec, project.seconds_per_image)
    n = min(n, settings.MAX_IMAGES_PER_PROJECT)
    words = word_budget(project.target_duration_sec)
    prompt = build_prompt(project, n, words)
    default_mood = project.niche.default_mood if project.niche else "mysterious"
    raw = gemini_client.generate_json(prompt, ScriptOut, temperature=0.8)
    data = clean_script(raw, default_mood, hook_scene_count_for(raw.scenes))
    problems = []
    if not count_ok(len(data.scenes), n):
        problems.append(f"your previous answer had {len(data.scenes)} scenes. Return EXACTLY {n} scenes")
    if not alternation_ok(data.scenes):
        problems.append(f"{same_kind_pairs(data.scenes)} neighbouring scenes had the same scene_kind. Strictly alternate "
                        "hero, fact, hero, fact... and keep fact scenes free of the main character")
    if problems:
        logger.warning("Script needs another pass (%s)", "; ".join(problems))
        retry = prompt + "\n\nIMPORTANT: " + ". ".join(problems) + "."
        raw = gemini_client.generate_json(retry, ScriptOut, temperature=0.7)
        data = clean_script(raw, default_mood, hook_scene_count_for(raw.scenes))
    if len(data.scenes) < 3:
        raise gemini_client.GeminiError("Gemini juda qisqa ssenariy qaytardi. Qayta urinib ko'ring.")
    return data


def authored_voice(s: SceneOut) -> dict:
    """Voice fields the script author chose for a scene (empty dict = leave it to the director)."""
    from ..models import Scene

    if not s.emotion:
        return {}
    emotion = s.emotion.strip().lower()
    out = {"emotion": emotion if emotion in Scene.Emotion.values else "neutral",
           "intensity": min(3, max(1, int(s.intensity or 2))),
           "pace": s.pace if s.pace in Scene.Pace.values else "normal"}
    if s.pause_after_ms:
        out["pause_after_ms"] = min(1500, max(0, int(s.pause_after_ms)))
    return out


@transaction.atomic
def save_script(project, data: ScriptOut) -> None:
    """Replace the project's scenes with the new script (hand-uploaded images are lost only if you regenerate)."""
    from ..models import Scene

    for s in project.scenes.all():
        for f in (s.image, s.audio, s.clip):
            if f:
                f.delete(save=False)
    project.scenes.all().delete()
    Scene.objects.bulk_create([
        Scene(project=project, order=i, narration=s.narration, image_prompt=s.image_prompt,
              beat_type=s.beat_type, fact_source=(s.fact_source or "")[:300],
              sfx=[{"tag": s.sfx_cue, "offset_ms": 0, "gain_db": settings.SFX_GAIN_DB}] if s.sfx_cue else [],
              **authored_voice(s))
        for i, s in enumerate(data.scenes, start=1)
    ])
    project.title = data.title.strip()[:300]
    project.description = data.description.strip()
    project.tags = data.tags
    project.script_json = data.model_dump()
    project.has_unrendered_changes = True
    project.save(update_fields=["title", "description", "tags", "script_json", "has_unrendered_changes", "updated_at"])


def total_words(project) -> int:
    return sum(len(s.narration.split()) for s in project.scenes.all())
