"""Topic normalization, hashing and duplicate detection (prompt 5.1 / 5.10 item 5)."""
from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Iterable

STOPWORDS = {
    "a", "an", "the", "of", "to", "in", "on", "for", "and", "or", "is", "are", "was", "were",
    "why", "how", "what", "when", "where", "who", "which", "do", "does", "did", "you", "your",
    "we", "i", "it", "its", "this", "that", "these", "those", "be", "been", "with", "about",
    "from", "by", "at", "as", "really", "actually", "ever", "so", "can", "could", "would", "t", "s",
    "they", "their", "them", "all", "our", "us", "we", "my", "there",
}
# Words that appear in almost every title of this niche carry no meaning for dedup
# ("What Did Ancient Humans ...?"), so they are ignored as well.
NICHE_COMMON = {"ancient", "human", "early", "prehistoric", "people", "our", "ancestor", "caveman", "cavemen", "stone", "age"}


def _stem(word: str) -> str:
    """Tiny, dependency-free stemmer: good enough to match 'cats'/'cat', 'eating'/'eat'."""
    for suffix in ("ing", "ies", "ed", "es", "s"):
        if len(word) > len(suffix) + 2 and word.endswith(suffix):
            return word[: -len(suffix)] + ("y" if suffix == "ies" else "")
    return word


def topic_tokens(text: str) -> list[str]:
    """Lowercase, strip accents/punctuation, drop stopwords, light-stem; sorted & unique."""
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    words = re.findall(r"[a-z0-9]+", text.lower())
    stems = {_stem(w) for w in words if w not in STOPWORDS}
    return sorted(stems - NICHE_COMMON)


def normalize_topic(text: str) -> str:
    return " ".join(topic_tokens(text))


def topic_hash(text: str) -> str:
    """Order-independent hash: 'Why do cats purr?' == 'cats purr why'."""
    return hashlib.sha1(normalize_topic(text).encode()).hexdigest()


def similarity(a: str, b: str) -> float:
    """0..1 similarity of two topics: max of token Jaccard and char-level ratio."""
    ta, tb = set(topic_tokens(a)), set(topic_tokens(b))
    if not ta or not tb:
        return 0.0
    jaccard = len(ta & tb) / len(ta | tb)
    ratio = SequenceMatcher(None, " ".join(sorted(ta)), " ".join(sorted(tb))).ratio()
    return max(jaccard, ratio)


@dataclass
class SimilarMatch:
    id: int
    topic: str
    score: float


def find_similar(topic: str, candidates: Iterable[tuple[int, str]], threshold: float = 0.6) -> list[SimilarMatch]:
    """Return candidates (id, topic) at or above `threshold`, best first."""
    h = topic_hash(topic)
    out: list[SimilarMatch] = []
    for cid, ctopic in candidates:
        score = 1.0 if topic_hash(ctopic) == h else similarity(topic, ctopic)
        if score >= threshold:
            out.append(SimilarMatch(cid, ctopic, round(score, 2)))
    return sorted(out, key=lambda m: m.score, reverse=True)


def find_similar_projects(topic: str, exclude_id: int | None = None, threshold: float = 0.6) -> list[SimilarMatch]:
    """Check the permanent project record for (near-)duplicate topics."""
    from ..models import Project

    qs = Project.objects.all()
    if exclude_id:
        qs = qs.exclude(pk=exclude_id)
    return find_similar(topic, qs.values_list("id", "topic"), threshold)
