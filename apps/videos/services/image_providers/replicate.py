"""Replicate image provider: pay-as-you-go API, thousands of community / official models.

POST https://api.replicate.com/v1/models/{owner}/{name}/predictions  (header "Prefer: wait" holds the request until done)
Model ids look like "black-forest-labs/flux-schnell" (an owner/name with a slash: that is how the app tells them
from Runware ids). Replicate does not send a price back, so the cost shown in the app is the model's list price
(MODEL_PRESETS) per picture; unknown models count as 0.
"""
from __future__ import annotations

import logging
import threading
import time

import requests
from django.conf import settings

from .base import ImageProvider, ImageProviderError, ImageProviderNotConfigured

logger = logging.getLogger(__name__)

API = "https://api.replicate.com/v1"
DEFAULT_MODEL = "black-forest-labs/flux-schnell"
RETRY_STATUSES = {429, 500, 502, 503, 504}


class ReplicateImageProvider(ImageProvider):
    name = "replicate"

    def __init__(self, token: str, model: str, max_retries: int = 4, timeout: int = 120, backoff_base: float = 3.0):
        self.token = token
        self.model = model
        self.max_retries = max_retries
        self.timeout = timeout
        self.backoff_base = backoff_base
        self.total_cost = 0.0
        self.images_done = 0
        self.last_cost: float | None = None
        self._lock = threading.Lock()
        self._no_aspect = False  # a model without an aspect_ratio input (e.g. recraft uses "size")

    @classmethod
    def from_settings(cls, model: str | None = None) -> "ReplicateImageProvider":
        token = (getattr(settings, "REPLICATE_API_TOKEN", "") or "").strip()
        if not token:
            raise ImageProviderNotConfigured(".env faylida REPLICATE_API_TOKEN to'ldirilmagan.")
        return cls(token, (model or getattr(settings, "REPLICATE_MODEL", "") or DEFAULT_MODEL).strip())

    def build_input(self, prompt: str, seed: int | None) -> dict:
        data = {"prompt": prompt[:3000]}
        if "recraft" in self.model:
            data["size"] = "1820x1024"
        elif not self._no_aspect:
            data["aspect_ratio"] = "16:9"
        if "flux" in self.model:
            data["output_format"] = "png"
        if seed is not None and "flux" in self.model:
            data["seed"] = int(seed) % 2147483647
        return data

    def generate(self, prompt: str, seed: int | None = None, references: list[bytes] | None = None) -> bytes:
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json", "Prefer": "wait=60"}
        url = f"{API}/models/{self.model}/predictions"
        last_error = ""
        for attempt in range(1, self.max_retries + 1):
            payload = {"input": self.build_input(prompt, seed)}
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            except requests.RequestException as exc:
                last_error = f"Tarmoq xatosi: {exc.__class__.__name__}"
            else:
                if resp.status_code in (200, 201):
                    return self._result(resp.json())
                last_error = self._error_text(resp)
                low = last_error.lower()
                if resp.status_code in (401, 403):
                    raise ImageProviderError("Replicate kaliti noto'g'ri (REPLICATE_API_TOKEN).")
                if resp.status_code == 402 or "insufficient credit" in low or "billing" in low:
                    raise ImageProviderError("Replicate hisobida kredit yo'q (credits limit). Billing'ni yoqing yoki to'ldiring.")
                if resp.status_code == 422 and "aspect_ratio" in low and not self._no_aspect:
                    self._no_aspect = True
                    continue
                if resp.status_code not in RETRY_STATUSES:
                    raise ImageProviderError(last_error)
                logger.warning("Replicate HTTP %s (attempt %s)", resp.status_code, attempt)
                wait = self._retry_after(resp)
                if wait:
                    time.sleep(min(wait, 30))
                    continue
            if attempt < self.max_retries:
                time.sleep(self.backoff_base ** attempt)
        raise ImageProviderError(f"{self.max_retries} urinishdan keyin ham bo'lmadi. {last_error}")

    # -- helpers
    def _result(self, pred: dict) -> bytes:
        deadline = time.time() + 120
        while pred.get("status") in ("starting", "processing") and time.time() < deadline:  # "wait" ran out: poll
            time.sleep(2)
            try:
                pred = requests.get(pred["urls"]["get"], headers={"Authorization": f"Bearer {self.token}"},
                                    timeout=self.timeout).json()
            except (requests.RequestException, KeyError, ValueError) as exc:
                raise ImageProviderError("Replicate natijasini olib bo'lmadi.") from exc
        if pred.get("status") != "succeeded":
            raise ImageProviderError(f"Replicate: {pred.get('status')} {str(pred.get('error') or '')[:200]}".strip())
        out = pred.get("output")
        out = out[0] if isinstance(out, list) and out else out
        if not isinstance(out, str) or not out.startswith("http"):
            raise ImageProviderError("Replicate javobida rasm yo'q.")
        try:
            r = requests.get(out, timeout=self.timeout)
            r.raise_for_status()
        except requests.RequestException as exc:
            raise ImageProviderError(f"Replicate rasmini yuklab bo'lmadi: {exc.__class__.__name__}") from exc
        from . import preset_price

        cost = preset_price(self.model) or 0.0
        with self._lock:
            self.total_cost += cost
            self.images_done += 1
        self.last_cost = cost
        return r.content

    @staticmethod
    def _retry_after(resp: requests.Response) -> float:
        try:
            return float(resp.headers.get("retry-after") or (resp.json().get("retry_after") or 0))
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def _error_text(resp: requests.Response) -> str:
        try:
            body = resp.json()
            return f"Replicate xatosi {resp.status_code}: {body.get('detail') or body.get('title') or body}"[:300]
        except ValueError:
            return f"Replicate xatosi {resp.status_code}: {resp.text[:200]}"
