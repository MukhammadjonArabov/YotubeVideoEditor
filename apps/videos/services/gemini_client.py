"""The only place that talks to Gemini (google-genai SDK).

* Model names come from .env (GEMINI_TEXT_MODEL ...), never hardcoded.
* Retries with exponential backoff on 429 / 5xx.
* `generate_json` asks for JSON matching a pydantic model, validates it, and retries once on invalid JSON.
* The API key is never logged.
"""
from __future__ import annotations

import json
import logging
import time
from typing import TypeVar

from django.conf import settings
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)
RETRY_CODES = {408, 429, 500, 502, 503, 504}


class GeminiError(RuntimeError):
    """Safe-to-show error (Uzbek)."""


class GeminiNotConfigured(GeminiError):
    pass


class GeminiBusy(GeminiError):
    """The model stayed overloaded (503) / rate-limited (429) after all retries -> try a fallback model."""


def is_configured() -> bool:
    return bool(settings.GEMINI_ENABLED and settings.GEMINI_API_KEY.strip() and settings.GEMINI_TEXT_MODEL.strip())


_client = None


def get_client():
    global _client
    if not settings.GEMINI_ENABLED:
        raise GeminiNotConfigured("Gemini o'chirilgan (.env: GEMINI_ENABLED=False).")
    if not settings.GEMINI_API_KEY.strip():
        raise GeminiNotConfigured(".env faylida GEMINI_API_KEY to'ldirilmagan.")
    if _client is None:
        from google import genai

        _client = genai.Client(api_key=settings.GEMINI_API_KEY.strip())
    return _client


def _text_model() -> str:
    model = settings.GEMINI_TEXT_MODEL.strip()
    if not model:
        raise GeminiNotConfigured(".env faylida GEMINI_TEXT_MODEL to'ldirilmagan (masalan: gemini-3.8-flash).")
    return model


def text_models() -> list[str]:
    """Primary model first, then GEMINI_FALLBACK_MODELS (comma separated), without duplicates."""
    models = [_text_model()]
    for m in (getattr(settings, "GEMINI_FALLBACK_MODELS", "") or "").split(","):
        m = m.strip()
        if m and m not in models:
            models.append(m)
    return models


def _with_fallback(run, what: str):
    """Call run(model) with each model in turn while the previous one is busy (503/429)."""
    models = text_models()
    last: GeminiError | None = None
    for i, model in enumerate(models):
        try:
            result = run(model)
            if i:
                logger.info("%s: used fallback model %s", what, model)
            return result
        except GeminiBusy as exc:
            last = exc
            logger.warning("%s: model %s busy, %s", what, model,
                           "trying fallback" if i + 1 < len(models) else "no fallback left")
        except GeminiError as exc:
            if i == 0:
                raise  # a real problem with the main model (bad key, bad name...) - report it
            logger.warning("%s: fallback model %s unusable: %s", what, model, exc)
    raise GeminiError(f"{last} Barcha modellar band ({', '.join(models)}). 5-10 daqiqadan keyin qayta urinib ko'ring.")


def _call(fn, what: str, max_retries: int = 5, backoff_base: float = 2.5):
    """Run fn() with retries on transient errors; map SDK errors to GeminiError."""
    from google.genai import errors

    last = ""
    for attempt in range(1, max_retries + 1):
        try:
            return fn()
        except errors.APIError as exc:
            code = getattr(exc, "code", None)
            msg = (getattr(exc, "message", "") or str(exc))[:300]
            last = f"Gemini xatosi {code}: {msg}"
            if code == 400 and "API key" in msg:
                raise GeminiError("GEMINI_API_KEY noto'g'ri.") from exc
            if code == 404:
                raise GeminiError(f"Model topilmadi — .env dagi model nomini tekshiring. ({msg})") from exc
            if code in (401, 403):
                raise GeminiError(f"Gemini ruxsat bermadi ({code}). Kalit yoki loyiha sozlamalarini tekshiring.") from exc
            if code not in RETRY_CODES:
                raise GeminiError(last) from exc
            logger.warning("%s: Gemini %s, retry %s/%s", what, code, attempt, max_retries)
        except Exception as exc:  # network etc.
            last = f"Gemini bilan aloqa xatosi: {exc.__class__.__name__}"
            logger.warning("%s: %s, retry %s/%s", what, exc.__class__.__name__, attempt, max_retries)
        if attempt < max_retries:
            time.sleep(backoff_base ** attempt)
    if "429" in last:
        last += " — limit tugagan bo'lishi mumkin."
    if "429" in last or "503" in last or "500" in last or "502" in last or "504" in last:
        raise GeminiBusy(last)
    raise GeminiError(last)


def generate_text(prompt: str, system: str | None = None, temperature: float = 0.7) -> str:
    from google.genai import types

    client = get_client()
    cfg = types.GenerateContentConfig(system_instruction=system, temperature=temperature)

    def run(model: str) -> str:
        resp = _call(lambda: client.models.generate_content(model=model, contents=prompt, config=cfg), "generate_text")
        return (resp.text or "").strip()

    return _with_fallback(run, "generate_text")


def _extract_json(text: str) -> str:
    text = (text or "").strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        text = text.rsplit("```", 1)[0]
    return text.strip()


def _mime(data: bytes) -> str:
    return "image/jpeg" if data[:3] == b"\xff\xd8\xff" else "image/png"


def generate_json(prompt: str, schema: type[T], system: str | None = None, temperature: float = 0.7,
                  images: list[bytes] | None = None, max_retries: int = 5) -> T:
    """Ask for JSON matching `schema`; validate with pydantic; one retry on invalid output.

    `images` (PNG/JPEG bytes) are sent along with the prompt (vision checks)."""
    from google.genai import types

    client = get_client()
    cfg = types.GenerateContentConfig(
        system_instruction=system,
        temperature=temperature,
        response_mime_type="application/json",
        response_schema=schema,
    )
    image_parts = [types.Part.from_bytes(data=b, mime_type=_mime(b)) for b in (images or [])]

    def run(model: str) -> T:
        last_err = ""
        for attempt in (1, 2):
            text = prompt if attempt == 1 else (
                f"{prompt}\n\nYour previous answer was not valid JSON for the schema ({last_err}). "
                "Return ONLY valid JSON that matches the schema."
            )
            contents = [*image_parts, text] if image_parts else text
            resp = _call(lambda: client.models.generate_content(model=model, contents=contents, config=cfg),
                         "generate_json", max_retries=max_retries)
            parsed = getattr(resp, "parsed", None)
            if isinstance(parsed, schema):
                return parsed
            try:
                return schema.model_validate(json.loads(_extract_json(resp.text)))
            except (ValueError, ValidationError) as exc:
                last_err = str(exc)[:300]
                logger.warning("Gemini returned invalid JSON (attempt %s): %s", attempt, last_err)
        raise GeminiError("Gemini to'g'ri JSON qaytarmadi. Qayta urinib ko'ring.")

    return _with_fallback(run, "generate_json")
