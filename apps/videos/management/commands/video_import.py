"""`python manage.py video_import script.json --minutes 20 --idea idea.txt --concept concept.md`

Imports a script that Claude wrote in Claude Code (see CLAUDE.md) as a new project (or replaces the
script of --project N), after checking it: scene count and word budget for the length, the hook,
hero/fact alternation, a source for every fact scene, and that it doesn't reuse phrases from earlier
videos. Then the director and the compliance check run, and the project waits for your approval.
"""
from __future__ import annotations

import json
import math
from itertools import takewhile
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from pydantic import ValidationError

from apps.videos import tasks
from apps.videos.models import ComplianceCheck, Niche, Project
from apps.videos.services import compliance, originality
from apps.videos.services import script as sc
from apps.videos.services.topics import find_similar_projects


def _text(value: str | None) -> str:
    """A file path or the text itself."""
    if not value:
        return ""
    p = Path(value)
    return p.read_text(encoding="utf-8").strip() if p.is_file() else value.strip()


def check_script(data: sc.ScriptOut, minutes: float, seconds_per_image: int, exclude_project_id: int | None = None,
                 words_per_minute: int | None = None, realistic: bool = False):
    """(problems that block the import, warnings). Unit-tested. `words_per_minute` and `realistic` come from the niche
    (Uzbek speech is slower, and photo-like niches have no hero/fact alternation)."""
    problems, warnings = [], []
    wpm = words_per_minute or settings.WORDS_PER_MINUTE
    scale = wpm / settings.WORDS_PER_MINUTE
    n = len(data.scenes)
    want = sc.expected_scene_count(round(minutes * 60), seconds_per_image)
    if abs(n - want) > max(3, want * 0.15):
        problems.append(f"sahnalar soni {n}, {minutes} daqiqa uchun ~{want} kerak "
                        f"({sc.hook_scene_target()} ta qisqa hook sahnasi + {seconds_per_image} s/rasm)")
    words = sum(len(s.narration.split()) for s in data.scenes)
    want_words = round(minutes * wpm)
    if abs(words - want_words) > want_words * 0.15:
        warnings.append(f"{words} so'z, {minutes} daqiqa uchun ~{want_words} kutiladi")
    if not realistic and not sc.alternation_ok(data.scenes):
        problems.append(f"qahramon/fakt almashinuvi buzilgan: {sc.same_kind_pairs(data.scenes)} ta qo'shni juft bir xil")
    no_source = [i for i, s in enumerate(data.scenes, 1) if s.scene_kind == "fact" and not (s.fact_source or "").strip()]
    if no_source:
        warnings.append(f"manbasi yo'q faktli sahnalar: {no_source[:20]}")
    hook = sum(1 for _ in takewhile(lambda s: s.beat_type == "hook", data.scenes))
    first = data.scenes[0].narration.lower() if data.scenes else ""
    if any(x in first for x in ("hello", "welcome", "in this video", "hey guys", "salom", "assalomu", "xush kelibsiz", "bu videoda")):
        problems.append("1-sahna salomlashish bilan boshlanadi - hook darhol mavzuga kirishi kerak")
    hook_words = sum(len(s.narration.split()) for s in data.scenes[:hook])
    if hook_words > round(110 * scale):
        warnings.append(f"hook ({hook} sahna) {hook_words} so'z - 40 soniyadan uzun bo'lishi mumkin")
    if hook < sc.hook_scene_target() - 4:
        problems.append(f"hook atigi {hook} sahna - rasmlar tez almashishi uchun ~{sc.hook_scene_target()} ta "
                        f"qisqa gap (har biri alohida sahna) kerak")
    hook_max = max(7, round(sc.HOOK_MAX_WORDS * scale))
    long_hook = [i for i, s in enumerate(data.scenes[:hook], 1) if len(s.narration.split()) > hook_max]
    if long_hook:
        warnings.append(f"hook sahnalari {long_hook} {hook_max} so'zdan uzun (2-3 soniyalik bitta gap bo'lsin)")
    for o in originality.script_overlap([s.narration for s in data.scenes], exclude_project_id):
        if o.share < 0.02:  # a handful of common phrases ("for the first time") is normal
            continue
        msg = f"#{o.project_id} «{o.topic}» bilan {o.share:.0%} umumiy ibora (masalan: «{o.examples[0]}»)"
        if o.share > settings.MAX_SCRIPT_OVERLAP:
            problems.append(msg)
        else:
            warnings.append(msg)
    if n > settings.MAX_IMAGES_PER_PROJECT:
        warnings.append(f"{n} sahna > MAX_IMAGES_PER_PROJECT={settings.MAX_IMAGES_PER_PROJECT}: oxirgilari rasmsiz qoladi")
    return problems, warnings


class Command(BaseCommand):
    help = "Check and import a Claude-written script JSON as a project (see CLAUDE.md)"

    def add_arguments(self, parser):
        parser.add_argument("json_path")
        parser.add_argument("--minutes", type=float, required=True, help="Target length in minutes")
        parser.add_argument("--seconds-per-image", type=int, default=None)
        parser.add_argument("--niche", default=None, help="Niche slug (e.g. teachai); default: the active niche")
        parser.add_argument("--idea", help="Your idea (Uzbek): text or a file path")
        parser.add_argument("--concept", help="The approved Uzbek concept: text or a file path")
        parser.add_argument("--project", type=int, help="Replace the script of this project instead of creating one")
        parser.add_argument("--dry-run", action="store_true", help="Only check, import nothing")
        parser.add_argument("--force", action="store_true", help="Import even if checks found blocking problems")
        parser.add_argument("--no-director", action="store_true")
        parser.add_argument("--no-compliance", action="store_true")

    def handle(self, *args, **o):
        try:
            data = sc.ScriptOut.model_validate(json.loads(Path(o["json_path"]).read_text(encoding="utf-8")))
        except (OSError, ValueError, ValidationError) as exc:
            raise CommandError(f"JSON o'qilmadi: {str(exc)[:500]}") from exc
        if o["niche"]:
            niche = Niche.objects.filter(slug=o["niche"]).first()
            if niche is None:
                raise CommandError(f"Nisha topilmadi: {o['niche']}")
        elif o["project"]:
            niche = Project.objects.get(pk=o["project"]).niche or Niche.active()
        else:
            niche = Niche.active()
        wpm = niche.words_per_minute if niche else settings.WORDS_PER_MINUTE
        realistic = bool(niche and niche.realistic)
        spi = o["seconds_per_image"] or (niche.default_seconds_per_image if niche else settings.DEFAULT_SECONDS_PER_IMAGE)
        data = sc.clean_script(data, niche.default_mood if niche else "mysterious",
                               sc.hook_scene_count_for(data.scenes, wpm / 60), realistic=realistic)

        problems, warnings = check_script(data, o["minutes"], spi, o["project"], wpm, realistic)
        similar = [m for m in find_similar_projects(data.title, exclude_id=o["project"]) if m.score >= 0.6]
        if similar:
            problems.append("mavzu takrorlanadi: " + "; ".join(f"#{m.id} {m.topic}" for m in similar))
        try:  # repeated studies / hook opener vs. the history of finished videos (warnings only)
            from apps.videos.services import history
            srcs = [s.fact_source for s in data.scenes if s.fact_source]
            warnings += history.script_reuse(srcs, data.scenes[0].narration if data.scenes else "", o["project"])
            for score, e, common in history.topic_overlap(data.title + " " + " ".join(data.tags or []), top=1):
                if score >= 0.5:
                    warnings.append(f"mazmun #{e['id']} «{e['title']}» ga yaqin ({score:.0%}): {', '.join(common[:6])}")
        except Exception as exc:
            warnings.append(f"video tarixi tekshirilmadi: {exc}")
        words = sum(len(s.narration.split()) for s in data.scenes)
        self.stdout.write(f"«{data.title}»: {len(data.scenes)} sahna, {words} so'z "
                          f"(~{words / wpm:.1f} daq), "
                          f"hook {sum(1 for s in data.scenes if s.beat_type == 'hook')} sahna")
        for w in warnings:
            self.stdout.write(self.style.WARNING(f"  ! {w}"))
        for p in problems:
            self.stdout.write(self.style.ERROR(f"  x {p}"))
        if problems and not o["force"]:
            raise CommandError("Tekshiruvdan o'tmadi (majburan: --force).")
        if o["dry_run"]:
            self.stdout.write(self.style.SUCCESS("Tekshiruv tugadi (--dry-run, hech narsa saqlanmadi)."))
            return

        if o["project"]:
            project = Project.objects.get(pk=o["project"])
            project.topic = data.title
        else:
            project = Project(niche=niche, topic=data.title,
                              tts_provider=("gemini" if niche.tts_voice.lower().startswith("gemini:") else "edge")
                              if (niche and niche.tts_voice) else settings.TTS_PROVIDER)
        project.target_duration_sec = math.ceil(o["minutes"] * 60)
        project.seconds_per_image = spi
        project.idea = _text(o["idea"]) or project.idea
        project.concept = _text(o["concept"]) or project.concept
        project.script_author = "claude"
        project.save()
        sc.save_script(project, data)
        ComplianceCheck.objects.filter(project=project).delete()
        project.set_status(Project.Status.SCRIPT_READY, f"Ssenariy (Claude) yuklandi: {len(data.scenes)} sahna, {words} so'z.")
        self.stdout.write(f"Loyiha #{project.pk} saqlandi.")

        if not o["no_director"]:
            self.stdout.write("Rejissyor ishlamoqda (1-4 daqiqa)...")
            self.stdout.write("  " + tasks._run_director(project))
        if not o["no_compliance"]:
            self.stdout.write("Qoidalar tekshiruvi (1-3 daqiqa)...")
            tasks._run_compliance(project, compliance)
            check = ComplianceCheck.objects.filter(project=project).first()
            if check:
                self.stdout.write(f"  Natija: {check.status}")
                for f in check.findings:
                    if f.get("status") != "pass":
                        self.stdout.write(f"  - {f.get('status')} | {f.get('category')} | {f.get('message')}")
        project.refresh_from_db()
        self.stdout.write(self.style.SUCCESS(f"Tayyor: http://127.0.0.1:8000/videolar/{project.pk}/ - {project.progress_message}"))
