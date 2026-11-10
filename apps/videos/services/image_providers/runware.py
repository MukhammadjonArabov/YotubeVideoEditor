"""Runware image provider: one API key, 200+ models (FLUX, Ideogram, Recraft, Krea, Nano Banana ...).

Docs: https://runware.ai/docs  -  POST https://api.runware.ai/v1 with a JSON *list* of tasks, Bearer key.
Pick the model with RUNWARE_MODEL (an AIR id such as "runware:100@1"; copy it from the model's page / Playground).
Price per image depends on the model: https://runware.ai/pricing?category=image
"""
from __future__ import annotations

import base64
import logging
import threading
import time
import uuid

import requests
from django.conf import settings

from .base import ImageProvider, ImageProviderError, ImageProviderNotConfigured

logger = logging.getLogger(__name__)

API_URL = "https://api.runware.ai/v1"
RETRY_STATUSES = {429, 500, 502, 503, 504}
SIZE = (1344, 768)  # 16:9, both sides multiples of 64 (what most models want); normalized to 1080p later
DEFAULT_MODEL = "runware:100@1"  # FLUX.1 schnell: the cheap default, change it in .env after testing other models


class RunwareImageProvider(ImageProvider):
    name = "runware"

    def __init__(self, api_key: str, model: str, steps: int = 0, use_references: bool = False,
                 max_retries: int = 4, timeout: int = 120, backoff_base: float = 2.0):
        self.api_key = api_key
        self.model = model
        self.steps = steps
        self.use_references = use_references
        self.max_retries = max_retries
        self.timeout = timeout
        self.backoff_base = backoff_base
        self._refused: set[str] = set()  # fields this model rejected (seed, referenceImages)
        self.last_cost: float | None = None
        self.total_cost = 0.0  # what this provider object spent so far (Runware's own per-image price)
        self.images_done = 0
        self._lock = threading.Lock()  # images are drawn in parallel threads

    @classmethod
    def from_settings(cls) -> "RunwareImageProvider":
        key = (getattr(settings, "RUNWARE_API_KEY", "") or "").strip()
        if not key:
            raise ImageProviderNotConfigured(".env faylida RUNWARE_API_KEY to'ldirilmagan.")
        return cls(key, (getattr(settings, "RUNWARE_MODEL", "") or DEFAULT_MODEL).strip(),
                   int(getattr(settings, "RUNWARE_STEPS", 0) or 0), bool(getattr(settings, "RUNWARE_USE_REFERENCES", False)))

    @property
    def supports_reference(self) -> bool:  # type: ignore[override]
        return self.use_references and "referenceImages" not in self._refused

    def build_task(self, prompt: str, seed: int | None, references: list[bytes] | None) -> dict:
        task = {"taskType": "imageInference", "taskUUID": str(uuid.uuid4()), "model": self.model,
                "positivePrompt": prompt[:3000], "width": SIZE[0], "height": SIZE[1], "numberResults": 1,
                "outputType": "base64Data", "outputFormat": "PNG", "includeCost": True}
        if self.steps:
            task["steps"] = self.steps
        if seed is not None and "seed" not in self._refused:
            task["seed"] = int(seed) % 4294967295
        if references and self.supports_reference:
            task["referenceImages"] = ["data:image/png;base64," + base64.b64encode(r).decode() for r in references[:4]]
        return task

    def generate(self, prompt: str, seed: int | None = None, references: list[bytes] | None = None) -> bytes:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        last_error = ""
        for attempt in range(1, self.max_retries + 1):
            task = self.build_task(prompt, seed, references)
            try:
                resp = requests.post(API_URL, headers=headers, json=[task], timeout=self.timeout)
            except requests.RequestException as exc:
                last_error = f"Tarmoq xatosi: {exc.__class__.__name__}"
            else:
                body = self._json(resp)
                if resp.status_code == 200 and not body.get("errors"):
                    return self._decode(body)
                last_error = self._error_text(resp, body)
                low = last_error.lower()
                if resp.status_code in (401, 403) or "invalid api key" in low or "unauthorized" in low:
                    raise ImageProviderError("Runware kaliti noto'g'ri yoki ruxsat yo'q (RUNWARE_API_KEY).")
                if resp.status_code == 402 or "insufficient" in low or "credit" in low or "balance" in low:
                    raise ImageProviderError("Runware balansi tugadi (credits limit). Hisobni to'ldiring.")
                if "seed" in low and "seed" in task:
                    self._refused.add("seed")
                    continue
                if "referenceimages" in low and "referenceImages" in task:
                    self._refused.add("referenceImages")
                    logger.warning("Runware model %s refused referenceImages", self.model)
                    continue
                if resp.status_code not in RETRY_STATUSES:
                    raise ImageProviderError(last_error)
                logger.warning("Runware HTTP %s (attempt %s)", resp.status_code, attempt)
            if attempt < self.max_retries:
                time.sleep(self.backoff_base ** attempt)
        raise ImageProviderError(f"{self.max_retries} urinishdan keyin ham bo'lmadi. {last_error}")

    # -- helpers
    @staticmethod
    def _json(resp: requests.Response) -> dict:
        try:
            data = resp.json()
        except ValueError:
            return {}
        return data if isinstance(data, dict) else {}

    def _decode(self, body: dict) -> bytes:
        items = body.get("data") or []
        item = items[0] if items else {}
        cost = float(item["cost"]) if item.get("cost") is not None else 0.0
        self.last_cost = cost
        with self._lock:
            self.total_cost += cost
            self.images_done += 1
        b64 = item.get("imageBase64Data")
        if b64:
            return base64.b64decode(b64)
        url = item.get("imageURL")
        if url:
            try:
                r = requests.get(url, timeout=self.timeout)
                r.raise_for_status()
                return r.content
            except requests.RequestException as exc:
                raise ImageProviderError(f"Runware rasmini yuklab bo'lmadi: {exc.__class__.__name__}") from exc
        raise ImageProviderError("Runware javobida rasm yo'q.")

    @staticmethod
    def _error_text(resp: requests.Response, body: dict) -> str:
        errs = body.get("errors") or []
        if errs and isinstance(errs[0], dict):
            e = errs[0]
            return f"Runware xatosi {resp.status_code}: {e.get('message') or e.get('code') or e}"[:300]
        return f"Runware xatosi {resp.status_code}: {resp.text[:200]}"
