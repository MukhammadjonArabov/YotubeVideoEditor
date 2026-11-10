"""Dubbed audio tracks (Russian, Spanish, French) + translated titles/description for English videos.

For each language: translate every scene's narration (a Claude-written file `scripts/translations/p<id>.<lang>.json`
wins; otherwise Google's free web translator), voice it with a free Edge TTS male voice, and mix it with the video's own
timing, SFX and music (`render.render_project(dub_audio=...)`). The .m4a is uploaded in YouTube Studio -> Languages ->
Audio. Files: media/projects/p<id>/dub/<lang>.m4a and <lang>.json (lines, titles, description).
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
import urllib.parse
import urllib.request
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)

LANGS = {
    "ru": {"name": "Русский", "uz": "Ruscha", "voice": "en-US-AndrewMultilingualNeural"},
    "es": {"name": "Español", "uz": "Ispancha", "voice": "es-ES-AlvaroNeural"},
    "fr": {"name": "Français", "uz": "Fransuzcha", "voice": "fr-FR-HenriNeural"},
}
GTX = "https://translate.googleapis.com/translate_a/single"
CHUNK_CHARS = 3500


class DubError(Exception):
    pass


def languages() -> list[str]:
    return [l for l in getattr(settings, "DUB_LANGUAGES", ["es", "fr"]) if l in LANGS]  # Russian dropped by the owner 2026-11-10


def wants_dub(project) -> bool:
    """English videos only (TeachAI is Uzbek, music has no narration)."""
    niche = getattr(project, "niche", None)
    lang = (getattr(niche, "language", "") or getattr(niche, "lang", "") or "en").lower()
    return lang.startswith("en") and "teachai" not in (getattr(niche, "name", "") or "").lower()


def dub_dir(project) -> Path:
    d = Path(settings.MEDIA_ROOT) / "projects" / f"p{project.pk}" / "dub"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ------------------------------------------------------------------ translation
def _gtx(text: str, lang: str) -> str:
    data = urllib.parse.urlencode({"client": "gtx", "sl": "en", "tl": lang, "dt": "t", "q": text}).encode()
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(GTX, data=data, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                parts = json.load(r)[0]
            return "".join(p[0] for p in parts if p and p[0])
        except Exception as exc:  # noqa: BLE001 - rate limits / network hiccups
            last = exc
            time.sleep(2 + attempt * 3)
    raise DubError(f"Tarjima ishlamadi ({lang}): {last}")


def translate_lines(lines: list[str], lang: str) -> list[str]:
    """Keeps one output line per input line (each narration is sent as one line of a block)."""
    out: list[str] = []
    block: list[str] = []

    def flush():
        if not block:
            return
        res = [x.strip() for x in _gtx("\n".join(block), lang).split("\n")]
        if len(res) != len(block):  # the translator merged/split lines: do this block one by one
            res = [_gtx(b, lang).strip() for b in block]
        out.extend(res)
        block.clear()

    for line in lines:
        line = " ".join((line or "").split()) or "."
        if sum(len(b) + 1 for b in block) + len(line) > CHUNK_CHARS:
            flush()
            time.sleep(0.5)
        block.append(line)
    flush()
    return out


def translation(project, lang: str, force: bool = False) -> dict:
    """{"lines": [...per scene...], "titles": [...], "description": "..."}; cached in dub/<lang>.json."""
    from . import kit

    path = dub_dir(project) / f"{lang}.json"
    scenes = list(project.scenes.order_by("order"))
    src_hash = hashlib.sha1("\n".join(s.narration for s in scenes).encode()).hexdigest()[:12]
    manual = Path(settings.BASE_DIR) / "scripts" / "translations" / f"p{project.pk}.{lang}.json"
    if path.exists() and not force:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("src") == src_hash and len(data.get("lines", [])) == len(scenes):
            if manual.exists():  # hand-written titles/description always win over the cached machine ones
                hand = json.loads(manual.read_text(encoding="utf-8"))
                changed = {k: hand[k] for k in ("titles", "description") if hand.get(k) and hand[k] != data.get(k)}
                if changed:
                    data.update(changed)
                    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
            return data
    data = json.loads(manual.read_text(encoding="utf-8")) if manual.exists() else {}
    if len(data.get("lines", [])) != len(scenes):
        data["lines"] = translate_lines([s.narration for s in scenes], lang)
        data["by"] = "google"
    else:
        data["by"] = "claude"
    k = kit.load_kit(project)
    if not data.get("titles") and k.get("titles"):
        data["titles"] = translate_lines(k["titles"], lang)
    if not data.get("description") and k.get("description"):
        paras = k["description"].split("\n")
        data["description"] = "\n".join(translate_lines(paras, lang) if any(p.strip() for p in paras) else paras)
    data["src"] = src_hash
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return data


# ------------------------------------------------------------------ voice + mix
def _voice_lines(project, lang: str, lines: list[str], progress) -> dict[int, Path]:
    from .tts.edge import EdgeTTSProvider

    tts = EdgeTTSProvider(LANGS[lang]["voice"], "+8%")
    folder = dub_dir(project) / f"{lang}_voice"
    folder.mkdir(exist_ok=True)
    out = {}
    scenes = list(project.scenes.order_by("order"))
    for n, (scene, text) in enumerate(zip(scenes, lines), start=1):
        h = hashlib.sha1(f"{LANGS[lang]['voice']}|{text}".encode()).hexdigest()[:10]
        f = folder / f"scene_{scene.order:03d}_{h}.mp3"
        for attempt in range(6):  # Edge TTS sometimes refuses for a minute ("NoAudioReceived"); wait it out
            if f.exists() and f.stat().st_size > 0:
                break
            try:
                tts.synthesize(text, f)
            except Exception:  # noqa: BLE001
                f.unlink(missing_ok=True)
                if attempt == 5:
                    raise
                time.sleep(15 * (attempt + 1))
        out[scene.order] = f
        if n % 25 == 0:
            progress(f"Dublyaj ({LANGS[lang]['uz']}): ovoz {n}/{len(scenes)}")
    return out


def make_dub(project, lang: str, progress=lambda m: None, force: bool = False) -> Path:
    from . import render

    if not project.final_video:
        raise DubError("Avval inglizcha video tayyor bo'lsin.")
    progress(f"Dublyaj ({LANGS[lang]['uz']}): tarjima...")
    data = translation(project, lang, force=force)
    voices = _voice_lines(project, lang, data["lines"], progress)
    out = dub_dir(project) / f"{lang}.m4a"
    progress(f"Dublyaj ({LANGS[lang]['uz']}): musiqa va SFX bilan yig'ilmoqda...")
    render.render_project(project, quality="final", progress=progress, captions=True, dub_audio=voices, dub_out=out)
    return out


def make_all(project, progress=lambda m: None, langs: list[str] | None = None) -> dict[str, str]:
    """Every configured language; one failing language does not stop the others. Returns {lang: "ok" | error}."""
    result = {}
    for lang in langs or languages():
        try:
            make_dub(project, lang, progress)
            result[lang] = "ok"
        except Exception as exc:  # noqa: BLE001
            logger.exception("Dub %s failed for project %s", lang, project.pk)
            result[lang] = str(exc)[:200]
    return result


def tracks(project) -> list[dict]:
    """For the video page: per language the audio URL and translated titles/description."""
    out = []
    base = Path(settings.MEDIA_ROOT) / "projects" / f"p{project.pk}" / "dub"
    for lang in languages():
        audio = base / f"{lang}.m4a"
        meta = base / f"{lang}.json"
        data = json.loads(meta.read_text(encoding="utf-8")) if meta.exists() else {}
        if not audio.exists() and not data:
            continue
        out.append({"code": lang, **LANGS[lang],
                    "audio_url": f"{settings.MEDIA_URL}projects/p{project.pk}/dub/{lang}.m4a" if audio.exists() else "",
                    "titles": data.get("titles", []), "description": data.get("description", "")})
    return out
