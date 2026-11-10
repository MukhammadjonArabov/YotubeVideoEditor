"""Music & sound-effect library: durations, tagging, starter pack import and the
selection logic used by the renderer (prompt 5.6)."""
from __future__ import annotations

import json
import logging
import re
import subprocess
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db.models import Max
from pydantic import BaseModel

from . import gemini_client

logger = logging.getLogger(__name__)

STARTER_DIR = Path(settings.BASE_DIR) / "starter_library"
AUDIO_EXTS = {".mp3", ".wav", ".ogg", ".m4a", ".aac", ".flac", ".opus"}


# ------------------------------------------------------------------ durations
def ffprobe_path() -> str:
    ff = settings.FFMPEG_PATH or "ffmpeg"
    p = Path(ff)
    if p.name.lower().startswith("ffmpeg"):
        return str(p.with_name(p.name.lower().replace("ffmpeg", "ffprobe")))
    return "ffprobe"


def audio_duration(path: str | Path) -> float:
    """Seconds. mutagen first (pure Python, no ffmpeg needed), ffprobe as fallback, 0 if unknown."""
    try:
        import mutagen

        info = mutagen.File(str(path))
        if info is not None and getattr(info, "info", None) and info.info.length:
            return round(float(info.info.length), 3)
    except Exception:  # noqa: BLE001
        pass
    try:
        out = subprocess.run(
            [ffprobe_path(), "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, timeout=30,
        )
        return round(float(out.stdout.strip()), 3)
    except (OSError, ValueError, subprocess.SubprocessError):
        return 0.0


# ------------------------------------------------------------------ tagging
def parse_tags(text: str) -> list[str]:
    return sorted({t.strip().lower() for t in re.split(r"[,;]", text or "") if t.strip()})


KEYWORDS = {
    # sfx
    "whoosh": "whoosh", "woosh": "whoosh", "swoosh": "swoosh", "swish": "swoosh", "riser": "riser", "rise": "riser",
    "boing": "boing", "spring": "boing", "impact": "impact", "hit": "impact", "punch": "impact", "boom": "impact",
    "thud": "impact", "ding": "ding", "bell": "ding", "chime": "ding", "confirm": "ding", "pop": "pop", "bubble": "pop",
    "pluck": "pop", "click": "click", "tap": "click", "select": "click",
    # music moods
    "calm": "calm", "relax": "calm", "peace": "calm", "ambient": "calm", "mystery": "mysterious",
    "mysterious": "mysterious", "secret": "mysterious", "dark": "mysterious", "happy": "playful",
    "fun": "playful", "playful": "playful", "ukulele": "playful", "tense": "tense", "suspense": "tense",
    "chase": "tense", "hope": "wholesome", "warm": "wholesome", "epic": "epic", "hero": "epic",
    "battle": "epic", "sad": "sad", "piano": "sad", "quirky": "quirky", "comedy": "quirky", "mischief": "quirky",
}


class SuggestedTags(BaseModel):
    tags: list[str]


def keyword_tags(filename: str, vocabulary: list[str]) -> list[str]:
    words = re.findall(r"[a-z]+", Path(filename).stem.lower())
    return sorted({KEYWORDS[w] for w in words if w in KEYWORDS and KEYWORDS[w] in vocabulary})


def suggest_tags(filename: str, kind: str, hint: str = "") -> list[str]:
    """kind='music' -> MUSIC_MOODS, 'sfx' -> SFX_TAGS. Gemini if configured, keyword rules otherwise."""
    vocab = settings.MUSIC_MOODS if kind == "music" else settings.SFX_TAGS
    tags = keyword_tags(filename, vocab)
    if gemini_client.is_configured():
        try:
            prompt = (
                f"Pick 1-4 tags for a {'background music track' if kind == 'music' else 'sound effect'} "
                f"named '{Path(filename).stem}'. {('Extra info: ' + hint) if hint else ''}\n"
                f"Allowed tags ONLY: {', '.join(vocab)}."
            )
            ai = gemini_client.generate_json(prompt, SuggestedTags, temperature=0.2).tags
            tags = sorted({t.strip().lower() for t in ai if t.strip().lower() in vocab} | set(tags))
        except gemini_client.GeminiError as exc:
            logger.info("Tag suggestion via Gemini skipped: %s", exc)
    return tags[:4]


# ------------------------------------------------------------------ create from upload / file
def add_track(uploaded, title: str = "", tags: list[str] | None = None, license_note: str = "", source: str = "upload"):
    from ..models import MusicTrack

    tags = tags or suggest_tags(uploaded.name, "music", title)
    track = MusicTrack(title=title or Path(uploaded.name).stem.replace("_", " "), mood_tags=tags,
                       license_note=license_note, source=source)
    track.file.save(Path(uploaded.name).name, uploaded, save=False)
    track.duration = audio_duration(track.file.path)
    track.save()
    return track


def add_sfx(uploaded, name: str = "", tags: list[str] | None = None):
    from ..models import SoundEffect

    tags = tags or suggest_tags(uploaded.name, "sfx", name)
    sfx = SoundEffect(name=name or Path(uploaded.name).stem.replace("_", " "), tags=tags)
    sfx.file.save(Path(uploaded.name).name, uploaded, save=False)
    sfx.duration = audio_duration(sfx.file.path)
    sfx.save()
    return sfx


def import_starter_pack() -> tuple[int, int]:
    """Load starter_library/manifest.json into the DB (skips files already imported)."""
    from ..models import MusicTrack, SoundEffect

    manifest = json.loads((STARTER_DIR / "manifest.json").read_text(encoding="utf-8"))
    m = s = 0
    for item in manifest["music"]:
        if MusicTrack.objects.filter(title=item["title"], source=item.get("source", "starter")).exists():
            continue
        with open(STARTER_DIR / item["file"], "rb") as fh:
            track = MusicTrack(title=item["title"], mood_tags=item["mood_tags"], source=item.get("source", "starter"),
                               license_note=item.get("license_note", ""))
            track.file.save(Path(item["file"]).name, File(fh), save=False)
        track.duration = audio_duration(track.file.path)
        track.save()
        m += 1
    for item in manifest["sfx"]:
        if SoundEffect.objects.filter(name=item["name"]).exists():
            continue
        with open(STARTER_DIR / item["file"], "rb") as fh:
            sfx = SoundEffect(name=item["name"], tags=item["tags"])
            sfx.file.save(Path(item["file"]).name, File(fh), save=False)
        sfx.duration = audio_duration(sfx.file.path)
        sfx.save()
        s += 1
    return m, s


def starter_pack_available() -> bool:
    return (STARTER_DIR / "manifest.json").exists()


# ------------------------------------------------------------------ selection (used by render)
def _has_tag(tags, tag: str) -> bool:
    return tag.lower() in [t.lower() for t in (tags or [])]


def pick_music(mood: str | None, exclude_project_id: int | None = None):
    """Tracks tagged with `mood` (fallback: any). Among them the least recently used by past projects."""
    from ..models import MusicTrack, Project

    tracks = list(MusicTrack.objects.all())
    if not tracks:
        return None
    matching = [t for t in tracks if mood and _has_tag(t.mood_tags, mood)] or tracks
    last_used = dict(
        Project.objects.exclude(pk=exclude_project_id).filter(music_track__isnull=False)
        .values("music_track").annotate(last=Max("created_at")).values_list("music_track", "last")
    )
    never = [t for t in matching if t.pk not in last_used]
    if never:
        return sorted(never, key=lambda t: t.pk)[0]
    return min(matching, key=lambda t: last_used[t.pk])


def pick_sfx(tag: str | None, seed: int = 0):
    """A sound effect whose tags contain `tag`, or None (never fails the render). `seed` rotates variants."""
    from ..models import SoundEffect

    if not tag:
        return None
    matches = [s for s in SoundEffect.objects.order_by("pk") if _has_tag(s.tags, tag)]
    if not matches:
        logger.info("No sound effect tagged '%s' - upload one in the Library", tag)
        return None
    return matches[seed % len(matches)]


def missing_sfx_tags() -> list[str]:
    from ..models import SoundEffect

    have = {t.lower() for s in SoundEffect.objects.all() for t in (s.tags or [])}
    return [t for t in settings.SFX_TAGS if t not in have]


def delete_media_file(obj) -> None:
    if obj.file:
        obj.file.delete(save=False)


__all__ = [
    "audio_duration", "parse_tags", "suggest_tags", "add_track", "add_sfx", "import_starter_pack",
    "pick_music", "pick_sfx", "missing_sfx_tags", "starter_pack_available",
]
