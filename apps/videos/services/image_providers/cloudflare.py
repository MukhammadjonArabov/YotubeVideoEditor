"""Cloudflare Workers AI image provider (FLUX models; free daily quota).

Docs: https://developers.cloudflare.com/workers-ai/models/flux-1-schnell/
POST https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}
JSON {"prompt": str, "steps": int (1..8)}  ->  {"result": {"image": "<base64 jpeg 1024x1024>"}, "success": true}
Note: flux-1-schnell rejects a "seed" field (HTTP 400, code 5006), so we only send it to other models
and drop it automatically if a model refuses it.
"""
from __future__ import annotations

import base64
import logging
import time

import requests
from django.conf import settings

from .base import ImageProvider, ImageProviderError, ImageProviderNotConfigured

logger = logging.getLogger(__name__)

API_URL = "https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/{model}"
RETRY_STATUSES = {429, 500, 502, 503, 504}
MAX_PROMPT_CHARS = 2048
NO_SEED_MODELS = {"@cf/black-forest-labs/flux-1-schnell"}
# FLUX.2 models take multipart/form-data, native width/height and up to 4 reference images
# (input_image_0..3) - that is what keeps the main character identical from scene to scene.
OUTPUT_SIZE = (1280, 720)


def parse_size(text: str) -> tuple[int, int] | None:
    """"1024x576" -> (1024, 576); anything else -> None (the default size)."""
    try:
        w, h = (int(x) for x in str(text or "").lower().split("x"))
    except ValueError:
        return None
    return (w, h) if w >= 256 and h >= 256 and w % 16 == 0 and h % 16 == 0 else None


def is_multipart_model(model: str) -> bool:
    return "flux-2" in model


class CloudflareImageProvider(ImageProvider):
    name = "cloudflare"

    def __init__(self, account_id: str, api_token: str, model: str, steps: int = 4,
                 max_retries: int = 4, timeout: int = 120, backoff_base: float = 2.0,
                 size: tuple[int, int] | None = None):
        self.account_id = account_id
        self.api_token = api_token
        self.size = size or OUTPUT_SIZE  # FLUX.2 is billed per output tile: a smaller picture costs less of the daily quota
        self.model = model
        self.steps = max(1, min(8, int(steps)))
        self.max_retries = max_retries
        self.timeout = timeout
        self.backoff_base = backoff_base

    @classmethod
    def from_settings(cls) -> "CloudflareImageProvider":
        account = (settings.CLOUDFLARE_ACCOUNT_ID or "").strip()
        token = (settings.CLOUDFLARE_API_TOKEN or "").strip()
        if not account or not token:
            raise ImageProviderNotConfigured(
                ".env faylida CLOUDFLARE_ACCOUNT_ID va CLOUDFLARE_API_TOKEN to'ldirilmagan."
            )
        main = cls(account, token, settings.CLOUDFLARE_IMAGE_MODEL, settings.CLOUDFLARE_IMAGE_STEPS)
        fact_model = (getattr(settings, "CLOUDFLARE_FACT_MODEL", "") or "").strip()
        fact_size = parse_size(getattr(settings, "CLOUDFLARE_FACT_SIZE", ""))
        if fact_model and (fact_model != settings.CLOUDFLARE_IMAGE_MODEL or fact_size):
            return SplitCloudflareProvider(main, cls(account, token, fact_model, settings.CLOUDFLARE_IMAGE_STEPS,
                                                     size=fact_size))
        return main

    @property
    def url(self) -> str:
        return API_URL.format(account=self.account_id, model=self.model)

    def build_payload(self, prompt: str, seed: int | None) -> dict:
        payload: dict = {"prompt": prompt[:MAX_PROMPT_CHARS], "steps": self.steps}
        if seed is not None and self.model not in NO_SEED_MODELS and not getattr(self, "_seed_refused", False):
            payload["seed"] = int(seed) % 2_147_483_647
        return payload

    @property
    def supports_reference(self) -> bool:
        return is_multipart_model(self.model) and not getattr(self, "_reference_refused", False)

    def build_multipart(self, prompt: str, seed: int | None, references: list[bytes] | None) -> tuple[dict, dict]:
        data = {"prompt": prompt[:MAX_PROMPT_CHARS], "steps": str(self.steps),
                "width": str(self.size[0]), "height": str(self.size[1])}
        if seed is not None and not getattr(self, "_seed_refused", False):
            data["seed"] = str(int(seed) % 2_147_483_647)
        files = {}
        if self.supports_reference:
            for i, ref in enumerate((references or [])[:4]):
                files[f"input_image_{i}"] = (f"ref{i}.png", ref, "image/png")
        return data, files

    def generate(self, prompt: str, seed: int | None = None, references: list[bytes] | None = None) -> bytes:
        headers = {"Authorization": f"Bearer {self.api_token}"}
        multipart = is_multipart_model(self.model)
        payload = self.build_payload(prompt, seed)
        form, files = self.build_multipart(prompt, seed, references) if multipart else ({}, {})
        last_error = ""
        for attempt in range(1, self.max_retries + 1):
            try:
                if multipart:
                    resp = requests.post(self.url, headers=headers, data=form, files=files or None, timeout=self.timeout)
                else:
                    resp = requests.post(self.url, headers=headers, json=payload, timeout=self.timeout)
            except requests.RequestException as exc:
                last_error = f"Tarmoq xatosi: {exc.__class__.__name__}"
                logger.warning("Cloudflare request failed (attempt %s): %s", attempt, exc.__class__.__name__)
            else:
                if resp.status_code == 200:
                    return self._decode(resp)
                last_error = self._error_text(resp)
                low = last_error.lower()
                if "daily free allocation" in low or "4006" in low:
                    raise ImageProviderError("Cloudflare kunlik bepul limiti tugadi (10 000 neuron). "
                                             "Limit Toshkent vaqti bilan 05:00 da yangilanadi.")
                if resp.status_code == 400 and "seed" in low and ("seed" in payload or "seed" in form):
                    self._seed_refused = True  # model doesn't take a seed - retry without it
                    payload.pop("seed", None)
                    form.pop("seed", None)
                    continue
                if resp.status_code == 400 and files and ("input_image" in low or "image" in low):
                    self._reference_refused = True  # model refused reference images - plain text-to-image
                    files = {}
                    logger.warning("Cloudflare model %s refused reference images", self.model)
                    continue
                if resp.status_code not in RETRY_STATUSES:
                    raise ImageProviderError(last_error)
                logger.warning("Cloudflare HTTP %s (attempt %s)", resp.status_code, attempt)
            if attempt < self.max_retries:
                time.sleep(self.backoff_base ** attempt)  # 2, 4, 8 s ...
        raise ImageProviderError(f"{self.max_retries} urinishdan keyin ham bo'lmadi. {last_error}")

    # -- helpers
    @staticmethod
    def _decode(resp: requests.Response) -> bytes:
        ctype = resp.headers.get("Content-Type", "")
        if ctype.startswith("image/"):  # some models return the image directly
            return resp.content
        try:
            data = resp.json()
            b64 = (data.get("result") or {}).get("image") or data.get("image")
        except ValueError as exc:
            raise ImageProviderError("Cloudflare javobi tushunarsiz (JSON emas).") from exc
        if not b64:
            raise ImageProviderError("Cloudflare javobida rasm yo'q.")
        return base64.b64decode(b64)

    @staticmethod
    def _error_text(resp: requests.Response) -> str:
        hints = {
            400: "So'rov noto'g'ri (prompt juda uzun yoki taqiqlangan so'z bo'lishi mumkin).",
            401: "Token noto'g'ri yoki muddati o'tgan (CLOUDFLARE_API_TOKEN).",
            403: "Tokenda Workers AI ruxsati yo'q yoki Account ID noto'g'ri.",
            404: "Model yoki Account ID topilmadi (CLOUDFLARE_IMAGE_MODEL / CLOUDFLARE_ACCOUNT_ID).",
            429: "Kunlik bepul limit tugadi yoki juda tez so'rov yuborildi. Ertaga davom eting.",
        }
        detail = ""
        try:
            errs = resp.json().get("errors") or []
            detail = "; ".join(str(e.get("message", e)) for e in errs)[:300]
        except ValueError:
            pass
        base = hints.get(resp.status_code, f"Cloudflare HTTP {resp.status_code}.")
        return f"{base} {detail}".strip()


class SplitCloudflareProvider(ImageProvider):
    """Two Cloudflare models in one provider (one daily quota): the main model draws the scenes that come with a
    character reference picture (the hero scenes: FLUX.2 keeps him looking the same), the cheap one draws all the
    others (facts, objects, places) - so a whole video fits into the free daily allowance."""

    name = "cloudflare"

    def __init__(self, hero: CloudflareImageProvider, other: CloudflareImageProvider):
        self.hero, self.other = hero, other

    @classmethod
    def from_settings(cls) -> "SplitCloudflareProvider":
        p = CloudflareImageProvider.from_settings()
        if not isinstance(p, SplitCloudflareProvider):
            raise ImageProviderNotConfigured("CLOUDFLARE_FACT_MODEL to'ldirilmagan.")
        return p

    @property
    def supports_reference(self) -> bool:  # type: ignore[override]
        return self.hero.supports_reference

    @property
    def notice(self) -> str:
        return ""

    def generate(self, prompt: str, seed: int | None = None, references: list[bytes] | None = None) -> bytes:
        if references and self.hero.supports_reference:
            return self.hero.generate(prompt, seed=seed, references=references)
        return self.other.generate(prompt, seed=seed)
