import io
import json
import tempfile
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from apps.videos.models import Niche, Project, Scene
from apps.videos.services import kit

TMP = tempfile.mkdtemp(prefix="kittest_")


def png(colour) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (1920, 1080), colour).save(buf, "PNG")
    return buf.getvalue()


@override_settings(MEDIA_ROOT=TMP)
class SlimSiteTests(TestCase):
    def setUp(self):
        self.p = Project.objects.create(topic="Why cats purr", title="Why Do Cats PURR?", status=Project.Status.DONE,
                                        actual_duration_sec=485, finished_at=timezone.now())
        for i, colour in enumerate(["#3a7bd5", "#d57b3a", "#3ad57b", "#d53a7b"], start=1):
            s = Scene.objects.create(project=self.p, order=i, narration=f"Line {i}.", image_prompt="x")
            s.image.save(f"s{i}.png", ContentFile(png(colour)), save=True)
        self.specs = [{"design": "hero", "text": "WHO HELPED HIM?", "hero": 1},
                      {"design": "object", "text": "NOT ALONE", "fact": 2, "badge": "50,000 YEARS"},
                      {"design": "split", "text": "WHO WAS HE?", "hero": 3, "fact": 4}]

    def test_dashboard_shows_stats_and_done_videos(self):
        r = self.client.get(reverse("videos:niche", args=["boshqa"]))
        self.assertContains(r, "Tayyor videolar")
        self.assertContains(r, "Why Do Cats PURR?")
        self.assertContains(r, "8:05")  # 485 s

    def test_front_page_lists_niches_and_each_niche_page_only_its_own_videos(self):
        n1 = Niche.objects.create(name="Qadim", slug="qadim", emoji="🪨", language="en")
        n2 = Niche.objects.create(name="TeachAI", slug="teachai", emoji="🤖", language="uz", is_active=False)
        Project.objects.create(topic="Old one", title="Old Title", niche=n1, status=Project.Status.DONE, actual_duration_sec=600,
                               finished_at=timezone.now())
        home = self.client.get(reverse("videos:home"))
        for text in ("Qadim", "TeachAI", "🤖", "Boshqa videolar"):
            self.assertContains(home, text)
        page1 = self.client.get(reverse("videos:niche", args=["qadim"]))
        self.assertContains(page1, "Old Title")
        self.assertNotContains(page1, "Why Do Cats PURR?")
        self.assertContains(self.client.get(reverse("videos:niche", args=["teachai"])), "Hozircha tayyor video yo'q")
        self.assertEqual(self.client.get(reverse("videos:niche", args=["yoq"])).status_code, 404)

    def test_dashboard_lists_work_in_progress(self):
        Project.objects.create(topic="Next", status=Project.Status.RENDERING, is_working=True, progress_message="Montaj 12/60")
        r = self.client.get(reverse("videos:niche", args=["boshqa"]))
        self.assertContains(r, "Montaj 12/60")
        self.assertContains(r, 'http-equiv="refresh"')

    def test_kit_command_draws_three_previews_and_the_page_shows_the_kit(self):
        specs = Path(TMP) / "specs.json"
        specs.write_text(json.dumps(self.specs), encoding="utf-8")
        desc = Path(TMP) / "desc.txt"
        desc.write_text("Hook line.\n\nSources:\n- X (2020)", encoding="utf-8")
        call_command("video_kit", str(self.p.pk), "--titles", "Title A", "Title B", "Title C", "--description-file", str(desc),
                     "--tags", "ice age, ancient humans", "--specs", str(specs))
        for i in (1, 2, 3):
            img = Image.open(kit.kit_dir(self.p) / f"preview_{i}.jpg")
            self.assertEqual(img.size, (1280, 720))
        page = self.client.get(reverse("videos:project_detail", args=[self.p.pk]))
        for text in ("Title A", "Title B", "Title C", "Sources:", "ice age, ancient humans", "WHO WAS HE?"):
            self.assertContains(page, text)
        self.assertContains(self.client.get(reverse("videos:niche", args=["boshqa"])), "nashr to'plami tayyor")

    def test_kit_needs_exactly_three_titles_and_previews(self):
        from django.core.management.base import CommandError

        with self.assertRaises(CommandError):
            call_command("video_kit", str(self.p.pk), "--titles", "only", "two")
        specs = Path(TMP) / "two.json"
        specs.write_text(json.dumps(self.specs[:2]), encoding="utf-8")
        with self.assertRaises(CommandError):
            call_command("video_kit", str(self.p.pk), "--specs", str(specs))

    def test_title_layout_splits_words_and_fits_the_box(self):
        self.assertEqual(kit.split_lines("who helped him?"), ["WHO HELPED", "HIM?"])
        self.assertEqual(kit.split_lines("NOT ALONE", 1), ["NOT ALONE"])
        img = Image.new("RGB", (kit.W, kit.H), "black")
        kit.title_block(img, "NO HEATER. NO JACKET.", (600, 70, 1230, 650))
        self.assertIsNotNone(img.getbbox())


@override_settings(MEDIA_ROOT=TMP)
class FlowPromptKitTests(TestCase):
    def test_three_flow_prompts_are_saved_and_shown(self):
        p = Project.objects.create(topic="X", title="X", status=Project.Status.DONE, finished_at=timezone.now())
        prompts = Path(TMP) / "flow.json"
        prompts.write_text(json.dumps([{"text": f"WORDS {i}", "prompt": f"Hand-drawn scene {i}. No text."} for i in (1, 2, 3)]), encoding="utf-8")
        call_command("video_kit", str(p.pk), "--flow-prompts", str(prompts))
        page = self.client.get(reverse("videos:project_detail", args=[p.pk]))
        for i in (1, 2, 3):
            self.assertContains(page, f"Hand-drawn scene {i}")
        self.assertContains(page, "Google Flow promptlari")
        prompts.write_text(json.dumps([{"text": "A", "prompt": "B"}]), encoding="utf-8")
        from django.core.management.base import CommandError

        with self.assertRaises(CommandError):
            call_command("video_kit", str(p.pk), "--flow-prompts", str(prompts))
