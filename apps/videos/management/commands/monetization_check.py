"""YouTube monetization check (rules: niches/monetization_rules.json).

    manage.py monetization_check --all          # every finished video, both niches
    manage.py monetization_check --music 5
    manage.py monetization_check --project 34
"""
from django.core.management.base import BaseCommand

from apps.videos.models import MusicVideo, Project
from apps.videos.services import monetization as mon

ICON = {"pass": "OK ", "warning": "!! ", "fail": "XX "}


class Command(BaseCommand):
    help = "Check videos against YouTube monetization rules."

    def add_arguments(self, parser):
        parser.add_argument("--all", action="store_true")
        parser.add_argument("--music", type=int, nargs="*", default=[])
        parser.add_argument("--project", type=int, nargs="*", default=[])
        parser.add_argument("--quiet", action="store_true", help="only problems")

    def handle(self, *args, **o):
        reports = []
        musics = MusicVideo.objects.filter(pk__in=o["music"]) if o["music"] else MusicVideo.objects.none()
        projects = Project.objects.filter(pk__in=o["project"]) if o["project"] else Project.objects.none()
        if o["all"]:
            musics = MusicVideo.objects.all()
            projects = Project.objects.exclude(final_video="")
        reports += [mon.check_music(m) for m in musics.order_by("pk")]
        reports += [mon.check_project(p) for p in projects.order_by("pk")]
        self.stdout.write(f"Qoidalar yangilangan: {mon.rules()['updated']}")
        for r in reports:
            self.stdout.write(f"\n[{r['status'].upper()}] {r['kind']} #{r['id']}: {r['title']}")
            for f in r["findings"]:
                if o["quiet"] and f["status"] == "pass":
                    continue
                self.stdout.write(f"  {ICON[f['status']]}{f['category']}: {f['message']}")
