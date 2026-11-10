"""Reference-channel research: YouTube Data API v3 import + Gemini style analysis + topic ideas."""
from __future__ import annotations

import logging
import re
from datetime import datetime

import requests
from django.conf import settings
from django.utils import timezone
from pydantic import BaseModel, Field

from . import gemini_client
from .topics import find_similar

logger = logging.getLogger(__name__)

API = "https://www.googleapis.com/youtube/v3"
MAX_VIDEOS = 40


class YouTubeError(RuntimeError):
    """Safe-to-show error (Uzbek)."""


# ------------------------------------------------------------------ parsing helpers
def parse_channel_input(text: str) -> dict:
    """Turn a URL / @handle / channel id into one of {"id": ...} / {"handle": ...} / {"username": ...}."""
    text = (text or "").strip()
    m = re.search(r"(UC[0-9A-Za-z_-]{22})", text)
    if m:
        return {"id": m.group(1)}
    m = re.search(r"@([0-9A-Za-z_.\-]{3,100})", text)
    if m:
        return {"handle": "@" + m.group(1)}
    m = re.search(r"youtube\.com/(?:c|user)/([^/?#]+)", text)
    if m:
        return {"username": m.group(1)}
    if re.fullmatch(r"[0-9A-Za-z_.\-]{3,100}", text):
        return {"handle": "@" + text}
    raise YouTubeError("Kanal manzilini tushunmadim. Masalan: https://www.youtube.com/@Inkexplainer96 yoki @Inkexplainer96")


def parse_iso_duration(value: str) -> int:
    """'PT1H2M3S' -> 3723 seconds."""
    m = re.fullmatch(r"P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?", value or "")
    if not m:
        return 0
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


def _dt(value: str | None):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


# ------------------------------------------------------------------ YouTube API
def _get(path: str, **params) -> dict:
    key = settings.YOUTUBE_API_KEY.strip()
    if not key:
        raise YouTubeError(".env faylida YOUTUBE_API_KEY to'ldirilmagan.")
    try:
        r = requests.get(f"{API}/{path}", params={**params, "key": key}, timeout=30)
    except requests.RequestException as exc:
        raise YouTubeError(f"YouTube bilan aloqa xatosi: {exc.__class__.__name__}") from exc
    if r.status_code != 200:
        try:
            reason = r.json()["error"]["errors"][0].get("reason", "")
        except (ValueError, KeyError, IndexError):
            reason = ""
        hints = {
            "quotaExceeded": "YouTube API kunlik limiti tugadi, ertaga qayta urinib ko'ring.",
            "keyInvalid": "YOUTUBE_API_KEY noto'g'ri.",
            "accessNotConfigured": "Google Cloud'da YouTube Data API v3 yoqilmagan.",
        }
        raise YouTubeError(hints.get(reason, f"YouTube API xatosi {r.status_code} {reason}".strip()))
    return r.json()


def fetch_channel(ref: dict) -> dict:
    params = {"part": "snippet,statistics,contentDetails"}
    if "id" in ref:
        params["id"] = ref["id"]
    elif "handle" in ref:
        params["forHandle"] = ref["handle"]
    else:
        params["forUsername"] = ref["username"]
    items = _get("channels", **params).get("items") or []
    if not items:
        raise YouTubeError("Bunday kanal topilmadi.")
    return items[0]


def fetch_videos(uploads_playlist_id: str, limit: int = MAX_VIDEOS) -> list[dict]:
    ids: list[str] = []
    page = None
    while len(ids) < limit:
        data = _get("playlistItems", part="contentDetails", playlistId=uploads_playlist_id,
                    maxResults=min(50, limit - len(ids)), **({"pageToken": page} if page else {}))
        ids += [i["contentDetails"]["videoId"] for i in data.get("items", [])]
        page = data.get("nextPageToken")
        if not page:
            break
    videos: list[dict] = []
    for i in range(0, len(ids), 50):
        videos += _get("videos", part="snippet,statistics,contentDetails", id=",".join(ids[i:i + 50])).get("items", [])
    return videos


def import_channel(channel) -> int:
    """Fill channel info + its latest videos. Returns number of videos stored."""
    from ..models import ChannelVideo

    raw = fetch_channel(parse_channel_input(channel.youtube_channel_id or channel.handle_or_url))
    sn, st = raw["snippet"], raw.get("statistics", {})
    channel.youtube_channel_id = raw["id"]
    channel.name = sn.get("title") or channel.name
    channel.handle = sn.get("customUrl", "")
    channel.description = sn.get("description", "")
    thumbs = sn.get("thumbnails", {})
    channel.thumbnail_url = (thumbs.get("medium") or thumbs.get("default") or {}).get("url", "")
    channel.subscriber_count = int(st["subscriberCount"]) if st.get("subscriberCount") else None
    channel.view_count = int(st.get("viewCount", 0) or 0)
    channel.video_count = int(st.get("videoCount", 0) or 0)
    channel.uploads_playlist_id = raw["contentDetails"]["relatedPlaylists"]["uploads"]
    channel.save()

    count = 0
    for v in fetch_videos(channel.uploads_playlist_id):
        vs, vst = v["snippet"], v.get("statistics", {})
        th = vs.get("thumbnails", {})
        ChannelVideo.objects.update_or_create(
            channel=channel, youtube_id=v["id"],
            defaults=dict(
                title=vs.get("title", "")[:300],
                description=vs.get("description", ""),
                published_at=_dt(vs.get("publishedAt")),
                duration_sec=parse_iso_duration(v.get("contentDetails", {}).get("duration", "")),
                view_count=int(vst.get("viewCount", 0) or 0),
                like_count=int(vst.get("likeCount", 0) or 0),
                comment_count=int(vst.get("commentCount", 0) or 0),
                thumbnail_url=(th.get("maxres") or th.get("high") or th.get("medium") or {}).get("url", ""),
            ),
        )
        count += 1
    return count


# ------------------------------------------------------------------ Gemini analysis
class StyleNotes(BaseModel):
    topic_formula: str = Field(description="Recurring topic formula of the channel")
    title_style: str = Field(description="How titles are written (length, question marks, caps...)")
    tone: str = Field(description="Narration tone and humour")
    typical_length: str = Field(description="Typical video length and pacing")
    what_performs_best: str = Field(description="Which kinds of videos get the most views and why")
    what_underperforms: str = Field(description="Which kinds of videos get fewer views")
    thumbnail_notes: str = Field(description="Best guess about thumbnail patterns from titles/descriptions")
    advice_for_original_channel: str = Field(description="How to be inspired without copying, 3-4 concrete tips")


class TopicIdea(BaseModel):
    topic: str = Field(description="English video title, under 70 characters")
    rationale: str = Field(description="One line in Uzbek: why this fits and why it can perform well")


class TopicIdeas(BaseModel):
    ideas: list[TopicIdea]


def _video_lines(channel, limit: int = MAX_VIDEOS) -> str:
    rows = []
    for v in channel.videos.all()[:limit]:
        rows.append(f"- {v.title} | {v.view_count:,} views | {v.duration_label} | {v.published_at:%Y-%m-%d}" if v.published_at
                    else f"- {v.title} | {v.view_count:,} views | {v.duration_label}")
    return "\n".join(rows)


def analyze_style(channel) -> str:
    """Store a readable Uzbek-labelled summary in channel.style_notes."""
    niche_brief = channel.niche.prompt_brief() if channel.niche else ""
    prompt = (
        "You analyse a YouTube channel to help a new, ORIGINAL channel in a similar niche.\n"
        f"{niche_brief}\n\nChannel: {channel.name}\nAbout: {channel.description[:800]}\n"
        f"Videos (title | views | length | date):\n{_video_lines(channel)}\n\n"
        "Write concise, specific notes. Answer in Uzbek (Latin script), keep English titles as they are."
    )
    notes = gemini_client.generate_json(prompt, StyleNotes, temperature=0.4)
    labels = [
        ("Mavzu formulasi", notes.topic_formula), ("Sarlavha uslubi", notes.title_style),
        ("Ohang", notes.tone), ("Uzunlik va temp", notes.typical_length),
        ("Eng yaxshi ishlaydi", notes.what_performs_best), ("Sust ishlaydi", notes.what_underperforms),
        ("Thumbnail", notes.thumbnail_notes), ("Nusxa ko'chirmasdan ilhomlanish", notes.advice_for_original_channel),
    ]
    channel.style_notes = "\n\n".join(f"{k}: {v.strip()}" for k, v in labels)
    channel.last_analyzed_at = timezone.now()
    channel.save(update_fields=["style_notes", "last_analyzed_at"])
    return channel.style_notes


def suggest_topics(channel, count: int = 10) -> list:
    """Ask Gemini for new topic ideas that avoid the channel's titles and my own projects."""
    from ..models import Project, SuggestedTopic

    own = list(Project.objects.values_list("pk", "topic"))
    theirs = list(channel.videos.values_list("pk", "title"))
    existing = list(SuggestedTopic.objects.exclude(status=SuggestedTopic.Status.DISMISSED).values_list("pk", "topic_text"))
    niche_brief = channel.niche.prompt_brief() if channel.niche else ""
    avoid = "\n".join(f"- {t}" for _, t in theirs + own + existing)
    prompt = (
        f"{niche_brief}\n\nReference channel style notes:\n{channel.style_notes[:3000]}\n\n"
        f"Suggest {count + 4} NEW video topics for my channel in this niche. They must follow the proven pattern "
        "but must NOT repeat or closely paraphrase any of these existing titles:\n"
        f"{avoid}\n\nPrefer everyday-life curiosity questions about ancient humans that a viewer would click. "
        "Each rationale is one short line in Uzbek."
    )
    ideas = gemini_client.generate_json(prompt, TopicIdeas, temperature=0.9).ideas
    created = []
    taken = theirs + own + existing
    for idea in ideas:
        topic = idea.topic.strip().strip('"')
        if not topic or find_similar(topic, taken, threshold=0.7):
            continue
        created.append(SuggestedTopic.objects.create(channel=channel, topic_text=topic[:300], rationale=idea.rationale.strip()))
        taken.append((0, topic))
        if len(created) >= count:
            break
    return created
