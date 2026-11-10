"""Try Runware models on a few scenes of a project and save the pictures side by side for comparison.

    ./venv/Scripts/python manage.py image_test --project 17 --scenes 1,6,13 --models runware:100@1,<another AIR id>

Pictures go to tmp/image_tests/<model>/scene_NNN.png (inside the project folder, on the project drive).
"""
from __future__ import annotations

import re
import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.videos.models import Project
from apps.videos.services import images
from apps.videos.services.image_providers import ImageProviderError
from apps.videos.services.image_providers.runware import RunwareImageProvider


class Command(BaseCommand):
    help = "Draw a few scenes with one or more Runware models and save them for comparison."

    def add_arguments(self, parser):
        parser.add_argument("--project", type=int, required=True)
        parser.add_argument("--scenes", default="1,2,3", help="comma separated scene numbers")
        parser.add_argument("--models", default="", help="comma separated Runware AIR ids (default: RUNWARE_MODEL)")
        parser.add_argument("--references", action="store_true", help="send the hero picture (models that accept it)")

    def handle(self, *args, **o):
        key = (settings.RUNWARE_API_KEY or "").strip()
        if not key:
            raise CommandError(".env faylida RUNWARE_API_KEY yo'q.")
        project = Project.objects.get(pk=o["project"])
        orders = [int(x) for x in o["scenes"].split(",") if x.strip()]
        models = [m.strip() for m in (o["models"] or settings.RUNWARE_MODEL).split(",") if m.strip()]
        ref = images.character_reference_bytes(project) if o["references"] else None
        total = 0.0
        for model in models:
            prov = RunwareImageProvider(key, model, int(settings.RUNWARE_STEPS or 0), use_references=bool(ref))
            folder = settings.TEMP_DIR / "image_tests" / re.sub(r"[^A-Za-z0-9._-]+", "_", model)
            folder.mkdir(parents=True, exist_ok=True)
            self.stdout.write(f"\n== {model}")
            for order in orders:
                scene = project.scenes.get(order=order)
                hero = images.mentions_main_character(scene.image_prompt)
                prompt = images.build_prompt(project.effective_style_guide, scene.image_prompt,
                                             project.character_description if hero else "")
                t0 = time.time()
                try:
                    raw = prov.generate(prompt, seed=7, references=[ref] if ref and hero else None)
                except ImageProviderError as exc:
                    self.stdout.write(self.style.ERROR(f"  {order}-sahna: {exc}"))
                    continue
                png = images.normalize_to_1080p(raw, mode="crop")
                (folder / f"scene_{order:03d}.png").write_bytes(png)
                cost = prov.last_cost or 0.0
                total += cost
                self.stdout.write(f"  {order}-sahna: {time.time() - t0:.1f} s, narx ${cost:.4f} -> {folder / f'scene_{order:03d}.png'}")
        self.stdout.write(self.style.SUCCESS(f"\nJami narx: ${total:.4f}"))
