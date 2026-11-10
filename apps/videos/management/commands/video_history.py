"""`python manage.py video_history` - rewrite reports/video_history.{json,md}: a short summary of every finished video.
`--check "topic"` shows which earlier videos cover the same content."""
from django.core.management.base import BaseCommand

from apps.videos.services import history


class Command(BaseCommand):
    help = "Write the history of finished videos (summary, chapters, hook, sources, keywords)"

    def add_arguments(self, parser):
        parser.add_argument("--check", nargs="*", default=[], help="Candidate topics to compare with the history")

    def handle(self, *args, **o):
        entries = history.write_history()
        self.stdout.write(f"Tarix yozildi: {len(entries)} ta video -> {history.MD_PATH}")
        for topic in o["check"]:
            self.stdout.write(f"\n{topic}")
            for score, e, common in history.topic_overlap(topic, entries):
                self.stdout.write(f"   {score:.0%}  #{e['id']} {e['title']} | umumiy: {', '.join(common[:8])}")
