"""Base class for image providers."""
from __future__ import annotations

import abc


class ImageProviderError(RuntimeError):
    """Generation failed (network, quota, bad response...). Message is safe to show in the UI."""


class ImageProviderNotConfigured(ImageProviderError):
    """Missing keys / unknown provider."""


class ImageProvider(abc.ABC):
    name: str = "base"

    @classmethod
    @abc.abstractmethod
    def from_settings(cls) -> "ImageProvider":
        """Build from django settings; raise ImageProviderNotConfigured if keys are missing."""

    supports_reference = False

    @abc.abstractmethod
    def generate(self, prompt: str, seed: int | None = None, references: list[bytes] | None = None) -> bytes:
        """Return raw image bytes for `prompt`. `references` = reference images (ignored if unsupported)."""
