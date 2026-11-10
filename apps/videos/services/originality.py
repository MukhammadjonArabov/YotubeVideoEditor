"""Is a new script really new? Compares its narration with every earlier script by shared
5-word phrases (after lower-casing and dropping punctuation). YouTube's inauthentic-content
policy is about templated, repetitive videos, so reused sentences across videos are a red flag.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

N = 5


def shingles(text: str, n: int = N) -> set[tuple[str, ...]]:
    words = re.findall(r"[a-z0-9']+", text.lower().replace("’", "'"))
    return {tuple(words[i:i + n]) for i in range(len(words) - n + 1)}


@dataclass
class Overlap:
    project_id: int
    topic: str
    share: float  # part of the new script's phrases that also appear in that project
    examples: list[str]


def script_overlap(narrations: list[str], exclude_project_id: int | None = None, top: int = 5) -> list[Overlap]:
    """Earlier projects that share the most 5-word phrases with `narrations`, highest first."""
    from ..models import Project

    new = shingles(" ".join(narrations))
    if not new:
        return []
    out = []
    projects = Project.objects.exclude(pk=exclude_project_id).prefetch_related("scenes")
    for p in projects:
        old = shingles(" ".join(s.narration for s in p.scenes.all()))
        common = new & old
        if common:
            out.append(Overlap(p.pk, p.topic, len(common) / len(new), [" ".join(c) for c in list(common)[:3]]))
    return sorted(out, key=lambda o: -o.share)[:top]
