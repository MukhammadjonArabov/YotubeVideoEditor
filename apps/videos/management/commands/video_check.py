"""`python manage.py video_check "Why did ancient humans ..."` - before proposing a new video:
how close is the topic to videos already made, what angles did they use, what works on reference channels.
Used by Claude in the idea -> concept step (see CLAUDE.md)."""
from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.videos.models import ChannelVideo, Niche, Project
from apps.videos.services import history
from apps.videos.services.topics import find_similar_projects


class Command(BaseCommand):
    help = "Compare candidate English topics with earlier videos and show what reference channels do well"

    def add_arguments(self, parser):
        parser.add_argument("topics", nargs="+", help="One or more candidate English topics/titles")
        parser.add_argument("--top", type=int, default=15, help="How many reference-channel hits to show")

    def handle(self, *args, **opts):
        niche = Niche.active()
        if niche:
            self.stdout.write(f"NISHA: {niche.name} ({niche.name_en})")
        for topic in opts["topics"]:
            similar = find_similar_projects(topic, threshold=0.35)
            verdict = "TAKRORLANADI" if any(m.score >= 0.6 for m in similar) else ("yaqin" if similar else "yangi")
            self.stdout.write(f"\n[{verdict}] {topic}")
            for m in similar:
                self.stdout.write(f"   {m.score:.2f}  #{m.id} {m.topic}")
            for score, e, common in history.topic_overlap(topic):
                mark = "MAZMUN TAKRORI?" if score >= 0.5 else "tarix"
                self.stdout.write(f"   {mark} {score:.0%} #{e['id']} {e['title']} | umumiy: {', '.join(common[:8])}")

        self.stdout.write(f"\nVIDEO TARIXI (to'liq xulosalar: {history.MD_PATH}):")
        for e in history.load_history():
            self.stdout.write(f"   #{e['id']} {e['title']} | {e['summary'][:120]}")

        self.stdout.write("\nOLDINGI VIDEOLAR (mavzu | hook'ning birinchi gapi):")
        for p in Project.objects.order_by("created_at").prefetch_related("scenes"):
            first = next((s.narration for s in p.scenes.all() if s.order == 1), "")
            self.stdout.write(f"   #{p.pk} [{p.status}] {p.topic} | {first[:110]}")

        self.stdout.write(f"\nNAMUNA KANALLAR, ENG KO'P KO'RILGAN {opts['top']} TA:")
        for v in ChannelVideo.objects.select_related("channel").order_by("-view_count")[:opts["top"]]:
            self.stdout.write(f"   {v.view_count:>11,} | {v.duration_label:>6} | {v.title[:90]}")
