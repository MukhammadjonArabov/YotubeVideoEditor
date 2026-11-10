"""Save the publish kit of a finished video and draw its 3 thumbnails.

  manage.py video_kit 19 --titles "Title A" "Title B" "Title C" --description-file scripts/x.description.txt \
      --tags "a, b, c" --specs scripts/x.previews.json

`--flow-prompts` is a JSON list of three {"text", "prompt"} objects (the same preview words with a Google Flow image prompt).
`--specs` is a JSON list of three objects, e.g.
  [{"design": "hero", "text": "WHO HELPED HIM?", "hero": 1, "fx": 0.4},
   {"design": "object", "text": "NOT ALONE", "fact": 14, "badge": "50,000 YEARS"},
   {"design": "split", "text": "WHO WAS HE?", "hero": 15, "fact": 2}]
`hero`/`fact` are scene numbers (1-based, the picture of that scene is used).
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.videos.models import Project
from apps.videos.services import kit


class Command(BaseCommand):
    help = "Publish kit: 3 titles, 1 description, tags, 3 thumbnail designs"

    def add_arguments(self, parser):
        parser.add_argument("project", type=int)
        parser.add_argument("--titles", nargs="+")
        parser.add_argument("--description-file")
        parser.add_argument("--tags", help="comma separated")
        parser.add_argument("--specs", help="JSON file with the 3 thumbnail specs")
        parser.add_argument("--flow-prompts", help="JSON file: list of 3 objects {\"text\": ..., \"prompt\": ...} for Google Flow")
        parser.add_argument("--show", action="store_true")

    def handle(self, *args, **o):
        try:
            project = Project.objects.get(pk=o["project"])
        except Project.DoesNotExist as exc:
            raise CommandError(f"Loyiha #{o['project']} topilmadi") from exc
        if o["titles"] and len(o["titles"]) != 3:
            raise CommandError("Aynan 3 ta sarlavha kerak")
        description = Path(o["description_file"]).read_text(encoding="utf-8").strip() if o["description_file"] else None
        tags = [t.strip() for t in o["tags"].split(",") if t.strip()] if o["tags"] else None
        if len(", ".join(tags or [])) > 500:
            raise CommandError("Teglar 500 belgidan oshmasin")
        flow = None
        if o["flow_prompts"]:
            flow = json.loads(Path(o["flow_prompts"]).read_text(encoding="utf-8"))
            if len(flow) != 3 or not all(f.get("prompt") and f.get("text") for f in flow):
                raise CommandError("Aynan 3 ta Flow promti kerak: {text, prompt}")
        kit.save_kit(project, titles=o["titles"], description=description, tags=tags, flow_prompts=flow)
        if o["specs"]:
            specs = json.loads(Path(o["specs"]).read_text(encoding="utf-8"))
            if len(specs) != 3:
                raise CommandError("Aynan 3 ta preview spetsifikatsiyasi kerak")
            built = kit.build_previews(project, specs)
            self.stdout.write(f"Preview: {[b['file'] for b in built]}")
        if o["show"] or not o["specs"]:
            data = kit.load_kit(project)
            self.stdout.write(json.dumps({k: v for k, v in data.items() if k != "description"}, ensure_ascii=False, indent=1))
        self.stdout.write(self.style.SUCCESS(f"Kit saqlandi: loyiha #{project.pk}"))
        from apps.videos.services import history
        try:
            history.write_history()
            self.stdout.write(f"Video tarixi yangilandi: {history.MD_PATH}")
        except Exception as exc:  # the kit is saved; history is a bonus
            self.stdout.write(self.style.WARNING(f"Video tarixi yozilmadi: {exc}"))
        from apps.videos.services import monetization
        report = monetization.check_project(project)
        self.stdout.write(f"Monetizatsiya tekshiruvi: {report['status'].upper()}")
        for f in report["findings"]:
            if f["status"] != "pass":
                self.stdout.write(f"  {f['status']}: {f['category']}: {f['message']}")
