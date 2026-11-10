"""History of finished videos: a short summary of each one, kept in reports/video_history.{json,md}.

Written after every publish kit (`video_kit`) and on demand (`manage.py video_history`). Used by `video_check` and
`video_import` to warn about repeated content: the same topic words, the same studies/sources, the same hook opener.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from django.conf import settings

from apps.videos.models import MusicVideo, Project
from apps.videos.services import kit
from apps.videos.services.topics import topic_tokens

HISTORY_DIR = Path(settings.BASE_DIR) / "reports"
JSON_PATH = HISTORY_DIR / "video_history.json"
MD_PATH = HISTORY_DIR / "video_history.md"
# Words that appear in almost every script and say nothing about the topic.
GENERIC = {"main", "character", "like", "subscribe", "thank", "minute", "comment", "next", "time", "see", "one",
           "two", "three", "just", "really", "know", "think", "people", "thing", "way", "day", "year", "even", "still", "here",
           "now", "get", "go", "make", "say", "tell", "want", "look", "back", "first", "last", "every", "much", "many", "most",
           "quick", "pause", "stay", "free", "second", "help", "curious", "read", "honest", "take", "probably", "maybe",
           "other", "more", "not", "but", "than", "less", "very", "about", "then", "also", "only", "same", "again", "mean",
           "part", "kind", "start", "keep", "come", "feel", "put", "let", "right", "good", "big", "small", "new", "old", "lot", "hard", "isn", "don", "didn", "doesn", "four", "five", "six", "seven",
           "eight", "nine", "ten", "twenty", "thirty", "forty", "fifty", "sixty", "hundred", "thousand", "each", "too", "happen"}


def _source_key(src: str) -> str:
    """'Huang, Yeomans ... (2017). It doesn't hurt...' -> 'huang 2017' (first author + year) for reuse checks."""
    m = re.match(r"\s*([A-Za-zÀ-ž'\-]+).*?\((\d{4})", src or "")
    return f"{m.group(1).lower()} {m.group(2)}" if m else (src or "").strip().lower()[:40]


def _summary(project, kit_data: dict) -> str:
    text = kit_data.get("description") or project.description or ""
    text = text.split("Chapters:")[0].split("Sources:")[0].strip()
    return re.sub(r"\s+", " ", text)[:600]


def _chapters(kit_data: dict) -> list[str]:
    desc = kit_data.get("description") or ""
    if "Chapters:" not in desc:
        return []
    block = desc.split("Chapters:", 1)[1].split("\n\n", 1)[0]
    return [re.sub(r"^\s*\d+:\d{2}(:\d{2})?\s*", "", ln).strip() for ln in block.splitlines() if ln.strip()]


def build_entry(project: Project) -> dict:
    scenes = list(project.scenes.order_by("order"))
    kit_data = kit.load_kit(project)
    words = Counter()
    for s in scenes:
        words.update(t for t in topic_tokens(s.narration) if t not in GENERIC and len(t) > 2 and not t.isdigit())
    sources = []
    for s in scenes:
        if s.fact_source and s.fact_source not in sources:
            sources.append(s.fact_source)
    hook = [s.narration for s in scenes if s.beat_type == "hook"][:4]
    return {
        "id": project.pk,
        "title": project.title or project.topic,
        "topic": project.topic,
        "titles": kit_data.get("titles") or [],
        "finished": project.finished_at.date().isoformat() if project.finished_at else None,
        "duration_sec": round(project.actual_duration_sec or 0),
        "summary": _summary(project, kit_data),
        "chapters": _chapters(kit_data),
        "hook": hook,
        "opener": hook[0] if hook else "",
        "sources": sources,
        "source_keys": sorted({_source_key(s) for s in sources}),
        "keywords": [w for w, _ in words.most_common(30)],
        "tags": kit_data.get("tags") or [],
    }


def finished_projects():
    return Project.objects.filter(status="done").exclude(final_video="").order_by("pk")


def write_history() -> list[dict]:
    entries = [build_entry(p) for p in finished_projects()]
    import sys
    if "test" in sys.argv[1:2]:  # never overwrite the real history from the test database
        return entries
    music = [{"id": m.pk, "title": getattr(m, "title", "") or str(m)} for m in MusicVideo.objects.order_by("pk")]
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps({"videos": entries, "music": music}, ensure_ascii=False, indent=1), encoding="utf-8")
    md = ["# Video tarixi", "", "Har bir tayyor video haqida qisqa xulosa. Avtomatik yoziladi (`video_kit`, `manage.py video_history`);",
          "`video_check` va `video_import` takroriy mavzu, manba va hook uchun shundan foydalanadi.", ""]
    for e in entries:
        md += [f"## #{e['id']} {e['title']}",
               f"- Tayyor: {e['finished'] or '-'} | {e['duration_sec'] // 60}:{e['duration_sec'] % 60:02d}",
               f"- Mazmuni: {e['summary'] or '-'}"]
        if e["chapters"]:
            md.append(f"- Bo'limlar: {'; '.join(e['chapters'])}")
        md.append(f"- Hook: {' / '.join(e['hook'])}")
        if e["source_keys"]:
            md.append(f"- Manbalar: {', '.join(e['source_keys'])}")
        md += [f"- Kalit so'zlar: {', '.join(e['keywords'][:15])}", ""]
    if music:
        md += ["## Musiqa videolari", ""] + [f"- #{m['id']} {m['title']}" for m in music] + [""]
    MD_PATH.write_text("\n".join(md), encoding="utf-8")
    return entries


def load_history() -> list[dict]:
    if not JSON_PATH.exists():
        return write_history()
    return json.loads(JSON_PATH.read_text(encoding="utf-8")).get("videos", [])


def topic_overlap(text: str, entries: list[dict] | None = None, top: int = 3) -> list[tuple[float, dict, list[str]]]:
    """Earlier videos whose content words (keywords, chapters, titles, tags) overlap the candidate text."""
    want = {t for t in topic_tokens(text) if t not in GENERIC and len(t) > 2}
    out = []
    for e in entries if entries is not None else load_history():
        theirs = set(e["keywords"][:15]) | set(topic_tokens(" ".join(e["chapters"] + e["titles"] + e["tags"] + [e["title"]])))
        common = sorted(want & theirs)
        if common:
            out.append((len(common) / max(len(want), 1), e, common))
    out.sort(key=lambda x: -x[0])
    return out[:top]


def script_reuse(sources: list[str], hook_first: str = "", exclude_id: int | None = None) -> list[str]:
    """Warnings for a new script: studies already used in earlier videos, and a hook opener that repeats one."""
    warnings = []
    keys = {_source_key(s) for s in sources if s}
    opener = " ".join(hook_first.lower().split()[:3])
    for e in load_history():
        if e["id"] == exclude_id:
            continue
        same = sorted(keys & set(e["source_keys"]))
        if same:
            warnings.append(f"#{e['id']} «{e['title']}» bilan bir xil manba: {', '.join(same)} (boshqa jihatini ayting)")
        if opener and " ".join(e["opener"].lower().split()[:3]) == opener:
            warnings.append(f"hook #{e['id']} bilan bir xil boshlanadi: «{e['opener'][:60]}»")
    return warnings
