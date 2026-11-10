"""Create (or update) a music video project from a JSON spec written by Claude.

    manage.py music_new scripts/music/rain_forest.json            # new project
    manage.py music_new scripts/music/rain_forest.json --project 3  # update prompts / kit of project 3

Spec: {"title", "music_prompt", "music_seconds"?, "target_minutes"?, "vocals"?, "flow_prompts": [{"title","prompt"}],
       "titles": [3 titles], "description", "tags": [...], "thumbnail_prompts": [{"text","prompt"}]}
The Musiqa niche is created on first use. Prompts are checked against niches/Musiqa.md rules.
"""
from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.videos.models import MusicVideo, Niche
from apps.videos.services import monetization, music_video as mvs

MAX_PROMPT = 4000


def music_niche() -> Niche:
    niche = Niche.objects.filter(kind="music").first()
    if niche:
        return niche
    return Niche.objects.create(
        name="Musiqa", name_en="Relaxing music", slug="musiqa", emoji="🎵", kind="music", language="en", is_active=False,
        description="Tinchlantiruvchi tabiat musiqasi: ayol ovozi (so'zsiz), oqayotgan suv, qush ovozlari. Bitta trek takrorlanib 20–30 daqiqalik video bo'ladi.")


def check_spec(spec: dict) -> list[str]:
    problems = []
    prompt = spec.get("music_prompt", "")
    if not prompt or len(prompt) > MAX_PROMPT:
        problems.append("music_prompt bo'sh yoki juda uzun.")
    low = prompt.lower()
    banned = ("sing about", "artist", "in the style of") if spec.get("lyrics") else ("lyrics:", "sing about", "artist", "in the style of")
    for bad in banned:
        if bad in low:
            problems.append(f"music_prompt'da '{bad}' bor: so'zlar yoki mavjud artist uslubi ishlatilmasin.")
    flows = spec.get("flow_prompts", [])
    if not 2 <= len(flows) <= mvs_max_clips():
        problems.append(f"flow_prompts soni 2–{mvs_max_clips()} bo'lishi kerak ({len(flows)}).")
    for i, f in enumerate(flows, 1):
        text = f.get("prompt", "")
        if len(text.split()) < 25:
            problems.append(f"{i}-Flow prompt juda qisqa.")
        if any(w in text.lower() for w in ("text", "logo", "watermark", "subtitle")) and "no text" not in text.lower():
            problems.append(f"{i}-Flow promptda yozuv/logotip so'ralgan bo'lishi mumkin.")
    titles = spec.get("titles", [])
    for t in titles:
        if len(t) >= 100:
            problems.append(f"Sarlavha juda uzun: {t[:40]}...")
    tags = ", ".join(spec.get("tags", []))
    if len(tags) > 500:
        problems.append(f"Teglar {len(tags)} belgi (500 dan oshmasin).")
    return problems


def mvs_max_clips() -> int:
    from apps.videos.views_music import MAX_CLIPS

    return MAX_CLIPS


class Command(BaseCommand):
    help = "Create or update a music video project from a JSON spec."

    def add_arguments(self, parser):
        parser.add_argument("spec")
        parser.add_argument("--project", type=int, default=None)

    def handle(self, *args, **opts):
        path = Path(opts["spec"])
        if not path.exists():
            raise CommandError(f"Fayl topilmadi: {path}")
        spec = json.loads(path.read_text(encoding="utf-8"))
        problems = check_spec(spec)
        if problems:
            raise CommandError("Spetsifikatsiya xatolari:\n- " + "\n- ".join(problems))
        if opts["project"]:
            mv = MusicVideo.objects.get(pk=opts["project"])
        else:
            mv = MusicVideo(niche=music_niche())
        mv.title = spec["title"][:200]
        mv.music_prompt = spec["music_prompt"]
        mv.music_seconds = int(spec.get("music_seconds", mv.music_seconds or 210))
        mv.target_minutes = int(spec.get("target_minutes", mv.target_minutes or 30))
        mv.vocals = bool(spec.get("vocals", True))
        mv.flow_prompts = [{"title": f.get("title") or f"Klip {i}", "prompt": f["prompt"]} for i, f in enumerate(spec["flow_prompts"], 1)]
        mv.kit = {"titles": spec.get("titles", []), "description": spec.get("description", ""), "tags": spec.get("tags", []),
                  "thumbnail_prompts": spec.get("thumbnail_prompts", [])}
        mv.save()
        self.stdout.write(self.style.SUCCESS(f"Musiqa loyihasi #{mv.pk}: {mv.title}"))
        self.stdout.write(f"Sahifa: http://127.0.0.1:8000/musiqa/{mv.pk}/")
        report = monetization.check_music(mv)
        self.stdout.write(f"Monetizatsiya tekshiruvi: {report['status'].upper()}")
        for f in report["findings"]:
            if f["status"] != "pass":
                self.stdout.write(f"  {f['status']}: {f['category']}: {f['message']}")
        self.stdout.write(f"ElevenLabs matni: {mvs.build_prompt(mv.music_prompt, mv.vocals)}")
