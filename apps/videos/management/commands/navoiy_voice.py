"""Voice a whole project with Navoiy TTS (the owner's cloned voice) outside the worker (it takes hours on this CPU),
then queue the render.

    manage.py navoiy_voice 31 [--redo] [--no-render]
"""
from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from apps.videos import tasks
from apps.videos.models import Project
from apps.videos.services.tts import navoiy


class Command(BaseCommand):
    help = "Voice a project with the local Navoiy TTS, then render it."

    def add_arguments(self, parser):
        parser.add_argument("project", type=int)
        parser.add_argument("--redo", action="store_true", help="Drop the existing voice first")
        parser.add_argument("--no-render", action="store_true")

    def handle(self, *args, **opts):
        project = Project.objects.get(pk=opts["project"])
        if not (project.niche and navoiy.is_navoiy(project.niche.tts_voice)):
            raise CommandError("Bu loyiha yo'nalishining ovozi navoiy:... emas.")
        scenes = [s for s in project.scenes.order_by("order") if s.narration.strip()]
        if opts["redo"]:
            for s in scenes:
                if s.audio:
                    s.audio.delete(save=False)
                    s.audio = ""
                    s.save(update_fields=["audio"])
        todo = [s for s in scenes if not s.audio]

        def progress(msg: str) -> None:
            Project.objects.filter(pk=project.pk).update(progress_message=msg)
            self.stdout.write(msg)

        Project.objects.filter(pk=project.pk).update(is_working=True)
        try:
            failed = navoiy.voice_scenes(project, todo, progress) if todo else []
        finally:
            Project.objects.filter(pk=project.pk).update(is_working=False)
        if failed:
            raise CommandError(f"Ovoz yaratilmadi: {failed}")
        self.stdout.write(self.style.SUCCESS(f"Ovoz tayyor: {len(todo)} ta sahna."))
        if not opts["no_render"]:
            project.refresh_from_db()
            tasks.enqueue("produce_video", project, "final", False)
            self.stdout.write("Montaj navbatga qo'yildi.")
