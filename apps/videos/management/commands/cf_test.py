"""`python manage.py cf_test` - check the image provider keys by drawing one test picture."""
from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.videos.services.image_providers import ImageProviderError, get_provider
from apps.videos.services.images import build_prompt, normalize_to_1080p


class Command(BaseCommand):
    help = "Draw one test image (python manage.py cf_test --provider cloudflare) and save it to media/"

    def add_arguments(self, parser):
        parser.add_argument("prompt", nargs="?", default="a caveman sitting by a campfire at night, looking at the stars, smiling")
        parser.add_argument("--provider", default=None, help="cloudflare (default: .env settings)")

    def handle(self, *args, **opts):
        try:
            provider = get_provider(opts["provider"])
            self.stdout.write(f"Provayder: {provider.name} ... rasm chizilmoqda (10-30 soniya)")
            raw = provider.generate(build_prompt(settings.DEFAULT_STYLE_GUIDE, opts["prompt"]), seed=42)
        except ImageProviderError as exc:
            raise CommandError(str(exc)) from exc
        out = Path(settings.MEDIA_ROOT) / f"test_image_{provider.name}.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(normalize_to_1080p(raw))
        self.stdout.write(self.style.SUCCESS(f"Tayyor! Rasmni oching: {out}"))
