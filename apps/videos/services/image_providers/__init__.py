"""Pluggable image generators. Main one: IMAGE_PROVIDER in .env; backups (used
automatically when the main one's free quota runs out): IMAGE_FALLBACK_PROVIDERS.

Every provider returns raw image bytes (any format Pillow can read); the caller
normalizes them to a 1920x1080 PNG.
"""
from __future__ import annotations

import logging

from django.conf import settings

from .base import ImageProvider, ImageProviderError, ImageProviderNotConfigured
from .cloudflare import CloudflareImageProvider
from .replicate import ReplicateImageProvider
from .runware import RunwareImageProvider

logger = logging.getLogger(__name__)

PROVIDERS: dict[str, type[ImageProvider]] = {
    "cloudflare": CloudflareImageProvider,
    "runware": RunwareImageProvider,
    "replicate": ReplicateImageProvider,
}

LABELS = {
    "cloudflare": "Cloudflare Workers AI",
    "gemini": "Gemini (pullik)",
    "runware": "Runware",
    "replicate": "Replicate",
}

QUOTA_WORDS = ("limit", "quota", "allocation", "pollen", "429", "402")


def is_quota_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(w in text for w in QUOTA_WORDS)


class FallbackImageProvider(ImageProvider):
    """Tries the providers in order. A provider whose quota ran out is skipped for the rest
    of the job; any other error only moves *this* image to the next provider."""

    name = "chain"

    def __init__(self, providers: list[ImageProvider]):
        self.providers = providers
        self.exhausted: set[str] = set()
        self.used: dict[str, int] = {}
        self.notice = ""

    @classmethod
    def from_settings(cls) -> "FallbackImageProvider":
        return build_chain()

    @property
    def active(self) -> ImageProvider:
        for p in self.providers:
            if p.name not in self.exhausted:
                return p
        return self.providers[-1]

    @property
    def supports_reference(self) -> bool:  # type: ignore[override]
        return self.active.supports_reference

    def generate(self, prompt: str, seed: int | None = None, references: list[bytes] | None = None) -> bytes:
        errors = []
        for p in self.providers:
            if p.name in self.exhausted:
                continue
            try:
                data = p.generate(prompt, seed=seed, references=references if p.supports_reference else None)
            except ImageProviderError as exc:
                errors.append(f"{LABELS.get(p.name, p.name)}: {exc}")
                if is_quota_error(exc) and p is not self.providers[-1]:
                    self.exhausted.add(p.name)
                    nxt = next((q for q in self.providers if q.name not in self.exhausted), None)
                    if nxt:
                        self.notice = (f"{LABELS.get(p.name, p.name)} limiti tugadi — "
                                       f"{LABELS.get(nxt.name, nxt.name)} bilan davom etildi.")
                        logger.warning("%s quota over, switching to %s", p.name, nxt.name)
                continue
            self.used[p.name] = self.used.get(p.name, 0) + 1
            return data
        raise ImageProviderError(" | ".join(errors) or "Rasm provayderi yo'q.")


def _names() -> list[str]:
    names = [settings.IMAGE_PROVIDER.strip().lower()]
    for n in (getattr(settings, "IMAGE_FALLBACK_PROVIDERS", "") or "").split(","):
        n = n.strip().lower()
        if n and n not in names:
            names.append(n)
    return names


def build_chain() -> ImageProvider:
    ready: list[ImageProvider] = []
    problems: list[str] = []
    for n in _names():
        cls = PROVIDERS.get(n)
        if cls is None:
            problems.append(f"'{n}' rasm provayderi yo'q (mavjud: {', '.join(PROVIDERS)}).")
            continue
        try:
            ready.append(cls.from_settings())
        except ImageProviderNotConfigured as exc:
            problems.append(str(exc))
    if not ready:
        raise ImageProviderNotConfigured(" ".join(problems) or "Rasm provayderi sozlanmagan.")
    return ready[0] if len(ready) == 1 else FallbackImageProvider(ready)


def get_provider(name: str | None = None) -> ImageProvider:
    """No name -> main provider plus backups. A name -> exactly that provider."""
    if name is None:
        return build_chain()
    cls = PROVIDERS.get(name.lower())
    if cls is None:
        raise ImageProviderNotConfigured(f"'{name}' rasm provayderi yo'q (mavjud: {', '.join(PROVIDERS)}).")
    return cls.from_settings()


# (Runware model id, label, price per image in USD, note). Prices: https://runware.ai/pricing?category=image
MODEL_PRESETS = [
    ("runware:100@1", "FLUX schnell (eng arzon, sifati past)", 0.003, ""),
    ("prunaai:p-image@ideogram", "P-Image-Ideogram", 0.003, "$5 balans kerak"),
    ("recraft:v4.1@flash", "Recraft V4.1 Flash (tekis illyustratsiya)", 0.007, "$5 balans kerak"),
    ("ideogram:4.5@0", "Ideogram 4.5 (promptga sodiq)", 0.008, "$5 balans kerak"),
    ("krea:krea@2-turbo", "Krea 2 Turbo", 0.015, "$5 balans kerak"),
    ("bytedance:seedream@5.0-flash", "Seedream 5.0 Flash", 0.019, "$5 balans kerak"),
    ("google:nano-banana@2-lite", "Nano Banana 2 Lite (sifatli)", 0.034, "$5 balans kerak"),
    # Replicate (model ids with a slash). List prices from replicate.com/pricing
    ("black-forest-labs/flux-schnell", "Replicate · FLUX schnell", 0.003, "Replicate"),
    ("black-forest-labs/flux-dev", "Replicate · FLUX dev", 0.025, "Replicate"),
    ("ideogram-ai/ideogram-v3-turbo", "Replicate · Ideogram v3 Turbo", 0.03, "Replicate"),
    ("recraft-ai/recraft-v3", "Replicate · Recraft v3", 0.04, "Replicate"),
    ("ideogram-ai/ideogram-v3-quality", "Replicate · Ideogram v3 Quality", 0.09, "Replicate"),
]


def preset_price(model_id: str) -> float | None:
    return next((p for m, _l, p, _n in MODEL_PRESETS if m == model_id), None)


def apply_model(provider: ImageProvider, model: str) -> ImageProvider:
    """Use the project's chosen model (empty = the .env default). A Replicate id (owner/name) puts a Replicate
    provider first and keeps the rest as backups; any other id is a Runware model."""
    model = (model or "").strip()
    if not model:
        return provider
    if "/" in model:
        try:
            first = ReplicateImageProvider.from_settings(model)
        except ImageProviderNotConfigured:
            return provider  # no Replicate key: keep the default provider rather than fail
        rest = list(getattr(provider, "providers", [provider]))
        return FallbackImageProvider([first, *rest])
    for p in getattr(provider, "providers", [provider]):
        if isinstance(p, RunwareImageProvider):
            p.model = model
    return provider


def spent(provider) -> tuple[float, int]:
    """(USD, images) spent so far by a provider or a fallback chain (providers that report a price)."""
    cost, n = 0.0, 0
    for p in getattr(provider, "providers", [provider]) if provider else []:
        cost += float(getattr(p, "total_cost", 0.0) or 0.0)
        n += int(getattr(p, "images_done", 0) or 0)
    return cost, n


def provider_status() -> tuple[bool, str]:
    """(is_ready, human message) for the UI."""
    try:
        p = get_provider()
    except ImageProviderNotConfigured as exc:
        return False, str(exc)
    if isinstance(p, FallbackImageProvider):
        main, *rest = [LABELS.get(q.name, q.name) for q in p.providers]
        return True, f"{main} (zaxira: {', '.join(rest)})"
    return True, LABELS.get(p.name, p.name)


__all__ = [
    "ImageProvider", "ImageProviderError", "ImageProviderNotConfigured", "FallbackImageProvider",
    "CloudflareImageProvider", "RunwareImageProvider", "ReplicateImageProvider", "MODEL_PRESETS", "apply_model", "preset_price", "spent", "get_provider", "provider_status", "is_quota_error",
]
