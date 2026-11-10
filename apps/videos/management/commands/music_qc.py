"""Quality report of music tracks.

    manage.py music_qc path/to/track.mp3       # check any audio file
    manage.py music_qc --project 3             # re-check every take of music project 3
"""
from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.videos.models import MusicVideo
from apps.videos.services import music_qc


def print_report(out, name: str, report: dict) -> None:
    m = report["metrics"]
    out.write(f"{name}: {report['score']}/100. {report['verdict']}")
    out.write(f"  uzunlik {m.get('duration')} s, {m.get('lufs')} LUFS, LRA {m.get('lra')}, cho'qqi {m.get('peak_db')} dBFS, "
              f"ulanish {m.get('seam_db')} dB, eng katta sakrash {m.get('max_jump_db')} dB")
    for i in report["issues"]:
        out.write(f"  {'XATO' if i['level'] == 'bad' else 'ogohlantirish'}: {i['text']}")


class Command(BaseCommand):
    help = "Automatic quality check of relaxing-music tracks."

    def add_arguments(self, parser):
        parser.add_argument("path", nargs="?")
        parser.add_argument("--project", type=int, default=None)

    def handle(self, *args, **opts):
        if opts["project"]:
            mv = MusicVideo.objects.get(pk=opts["project"])
            for take in mv.takes.all():
                take.qc = music_qc.analyze(Path(take.file.path), take.duration)
                take.score = take.qc["score"]
                take.save(update_fields=["qc", "score"])
                print_report(self.stdout, f"variant #{take.pk}{' (tanlangan)' if take.is_selected else ''}", take.qc)
        elif opts["path"]:
            path = Path(opts["path"])
            if not path.exists():
                raise CommandError(f"Fayl topilmadi: {path}")
            print_report(self.stdout, path.name, music_qc.analyze(path))
        else:
            raise CommandError("Fayl yo'lini yoki --project ko'rsating.")
