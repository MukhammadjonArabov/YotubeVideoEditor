"""Best-effort watcher for YouTube's public policy pages (prompt 5.9).

NOT a compliance guarantee: pages change structure, some are rendered with JS and
YouTube publishes no machine-readable changelog. A failed check is recorded as a
failure - never as "no changes".
"""
from __future__ import annotations

import difflib
import hashlib
import logging
import re

import requests
from django.conf import settings
from django.utils import timezone

from . import gemini_client

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/126.0 Safari/537.36 AutoExplainer-policy-watch",
    "Accept-Language": "en-US,en;q=0.9",
}
MIN_TEXT_CHARS = 400  # less than this = probably a JS shell / error page


class PolicyFetchError(RuntimeError):
    pass


def clean_text(html: str) -> str:
    """Main readable text of a help-centre page, without navigation/boilerplate."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "nav", "header", "footer", "form", "iframe", "button"]):
        tag.decompose()
    for sel in ["[role=navigation]", "[role=banner]", "[role=contentinfo]", ".feedback", ".hcfe-footer"]:
        for tag in soup.select(sel):
            tag.decompose()
    main = soup.find("article") or soup.find("main") or soup.find(attrs={"role": "main"}) or soup.body or soup
    text = main.get_text("\n", strip=True)
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines()]
    noise = re.compile(r"^(Was this helpful\?|Yes|No|Submit|Send feedback|Help Center|Community|Privacy Policy|"
                       r"Terms of Service|Need more help\?|Try these next steps:)$", re.I)
    return "\n".join(ln for ln in lines if ln and not noise.match(ln))


def fetch_text(url: str) -> str:
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
    except requests.RequestException as exc:
        raise PolicyFetchError(f"Sahifa yuklanmadi: {exc.__class__.__name__}") from exc
    if r.status_code != 200:
        raise PolicyFetchError(f"Sahifa HTTP {r.status_code} qaytardi.")
    text = clean_text(r.text)
    if len(text) < MIN_TEXT_CHARS:
        raise PolicyFetchError("Sahifadan matn olinmadi (JavaScript bilan chiziladigan sahifa bo'lishi mumkin).")
    return text


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def diff_excerpt(old: str, new: str, limit: int = 60) -> str:
    lines = [ln for ln in difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm="", n=0)
             if (ln.startswith("+") or ln.startswith("-")) and not ln.startswith(("+++", "---"))]
    return "\n".join(lines[:limit])


def summarize_change(label: str, old: str, new: str) -> str:
    diff = diff_excerpt(old, new, limit=200)
    if gemini_client.is_configured():
        try:
            return gemini_client.generate_text(
                f"The YouTube policy page '{label}' changed. Below is a line diff (- removed, + added).\n\n{diff[:12000]}\n\n"
                "Explain in plain Uzbek (Latin script), in 3-6 short bullet points, what likely changed and what it "
                "means for a faceless, AI-narrated educational explainer channel. If the change looks cosmetic "
                "(formatting, links, dates), say so. Do not invent rules that are not in the diff.",
                temperature=0.2,
            )
        except gemini_client.GeminiError as exc:
            logger.warning("Policy summary via Gemini failed: %s", exc)
    added = sum(1 for ln in diff.splitlines() if ln.startswith("+"))
    removed = sum(1 for ln in diff.splitlines() if ln.startswith("-"))
    return (f"Sahifa o'zgardi: {added} qator qo'shildi, {removed} qator olib tashlandi. "
            f"(Gemini ulanmagan, shuning uchun avtomatik xulosa yo'q.)\n\n{diff_excerpt(old, new, 25)}")


def check_document(doc) -> str:
    """Fetch + compare one PolicyDocument. Returns 'first' | 'same' | 'changed' | 'error'."""
    from ..models import PolicyChangeNote

    now = timezone.now()
    try:
        text = fetch_text(doc.url)
    except PolicyFetchError as exc:
        doc.last_checked_at, doc.last_check_ok, doc.last_error = now, False, str(exc)
        doc.save(update_fields=["last_checked_at", "last_check_ok", "last_error"])
        return "error"
    h = text_hash(text)
    result = "same"
    if not doc.last_content_hash:
        result = "first"
    elif h != doc.last_content_hash:
        result = "changed"
        PolicyChangeNote.objects.create(policy_document=doc, plain_summary=summarize_change(doc.label, doc.last_text, text))
        doc.last_changed_at = now
    doc.last_content_hash, doc.last_text = h, text
    doc.last_checked_at, doc.last_check_ok, doc.last_error = now, True, ""
    doc.save()
    return result


def check_all() -> dict:
    from ..models import PolicyDocument

    results = {}
    for doc in PolicyDocument.objects.filter(enabled=True):
        results[doc.pk] = check_document(doc)
    return results


def ensure_schedule() -> None:
    """Create/refresh the recurring django-q2 job (every POLICY_CHECK_INTERVAL_DAYS days)."""
    from django_q.models import Schedule

    days = max(1, int(settings.POLICY_CHECK_INTERVAL_DAYS))
    Schedule.objects.update_or_create(
        name="policy-watch",
        defaults=dict(func="apps.videos.tasks.policy_check_all", schedule_type=Schedule.MINUTES,
                      minutes=days * 24 * 60, repeats=-1),
    )
