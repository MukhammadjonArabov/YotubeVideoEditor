import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from apps.videos.models import Niche, Project
from apps.videos.services import manual_images as mi
from apps.videos.services import scenes as ops


def png(colour="red", size=(1024, 1024)):
    buf = io.BytesIO()
    Image.new("RGB", size, colour).save(buf, "PNG")
    return buf.getvalue()


class MatchingTests(TestCase):
    def setUp(self):
        self.p = Project.objects.create(topic="Manual", style_guide="STYLE")
        prompts = ["the main character running through a dark forest at night", "a mammoth drinking from a river",
                   "a map of Africa with arrows", "a campfire under stars"] + [f"scene {i}" for i in range(5, 13)]
        self.scenes = [ops.add_scene(self.p, narration=f"n{i}", image_prompt=t) for i, t in enumerate(prompts, 1)]

    def test_numbers_in_names(self):
        v = set(range(1, 13))
        self.assertEqual(mi.number_from_name("001.png", v), 1)
        self.assertEqual(mi.number_from_name("scene_012.jpg", v), 12)
        self.assertEqual(mi.number_from_name("image (7).png", v), 7)
        self.assertEqual(mi.number_from_name("flow_2026-09-27_18-42-05_003.png", v), 3)
        self.assertEqual(mi.number_from_name("Flow 2026 09 27 image 11.png", v), 11)
        self.assertEqual(mi.number_from_name("7_the main character runs 2 miles.png", v), 7)
        self.assertEqual(mi.number_from_name("12 - scene 3.jpg", v), 12)
        self.assertIsNone(mi.number_from_name("cat.png", v))
        self.assertIsNone(mi.number_from_name("099.png", v))

    def test_auto_match_and_conflicts(self):
        r = mi.match_files(["002.png", "1.jpg", "a_mammoth_drinking_from_a_river.png", "a map of africa with arrows.png",
                            "notes.txt", "x.png"], self.scenes)
        self.assertEqual(r.assigned["1.jpg"], 1)
        self.assertEqual(r.assigned["002.png"], 2)
        self.assertIn("a_mammoth_drinking_from_a_river.png", r.unmatched)  # scene 2 already taken by its number
        self.assertEqual(r.assigned["a map of africa with arrows.png"], 3)
        self.assertIn("x.png", r.unmatched)
        self.assertEqual(r.skipped, ["notes.txt"])

    def test_order_mode_natural_sort(self):
        r = mi.match_files(["img10.png", "img2.png", "img1.png"], self.scenes, mode="order", start=3)
        self.assertEqual(r.assigned, {"img1.png": 3, "img2.png": 4, "img10.png": 5})
        many = [f"{i}.png" for i in range(1, 15)]
        self.assertEqual(len(mi.match_files(many, self.scenes, mode="order").unmatched), 2)

    def test_prompts_have_character_and_one_per_line(self):
        n = Niche.objects.create(name="N", character_description="round white head, brown fur tunic", is_active=False)
        self.p.niche = n
        self.p.save()
        txt = mi.prompts_txt(self.p)
        lines = txt.strip().split("\n")
        self.assertEqual(len(lines), 12)
        self.assertTrue(lines[0].startswith("the main character running"))  # scene first -> distinct file names
        self.assertIn("round white head", lines[0])
        self.assertNotIn("round white head", lines[1])
        named = mi.prompts_txt(self.p, character_name="main_hero").split("\n")
        self.assertTrue(named[0].startswith("main_hero running"))
        self.assertNotIn("round white head", named[0])
        self.assertEqual(mi.clean_character_name("main hero"), "main_hero")
        self.assertEqual(mi.clean_character_name("hero!"), "")
        self.assertTrue(mi.prompts_txt(self.p, numbered=True).startswith("001 | "))


class UploadViewTests(TestCase):
    def setUp(self):
        self.p = Project.objects.create(topic="Upload", style_guide="S")
        self.a = ops.add_scene(self.p, narration="a", image_prompt="one")
        self.b = ops.add_scene(self.p, narration="b", image_prompt="two")

    def tearDown(self):
        for s in self.p.scenes.all():
            if s.image:
                s.image.delete()




class HookVideoTests(TestCase):
    def setUp(self):
        from apps.videos.services import hook_video

        self.hv = hook_video
        self.p = Project.objects.create(topic="Hook video")
        for i in range(1, 6):
            s = ops.add_scene(self.p, narration=f"n{i}", image_prompt="the main character stares at a glowing cave" if i % 2 else "a skull")
            s.beat_type = "hook" if i <= 3 else "normal"
            s.save(update_fields=["beat_type"])
        self.scenes = list(self.p.scenes.all())

    def test_only_hook_scenes_take_videos(self):
        r = self.hv.match_files(["001.mp4", "002.mov", "004.mp4", "notes.txt", "cat.mp4"], self.scenes)
        self.assertEqual(r.assigned, {"001.mp4": 1, "002.mov": 2})
        self.assertEqual(sorted(r.unmatched), ["004.mp4", "cat.mp4"])  # 4 is not a hook scene
        self.assertEqual(r.skipped, ["notes.txt"])

    def test_order_mode(self):
        r = self.hv.match_files(["b2.mp4", "b10.mp4", "b1.mp4", "b4.mp4"], self.scenes, mode="order")
        self.assertEqual(r.assigned, {"b1.mp4": 1, "b2.mp4": 2, "b4.mp4": 3})
        self.assertEqual(r.unmatched, ["b10.mp4"])

    def test_prompts_cover_hook_only_and_describe_motion(self):
        rows = self.hv.prompt_rows(self.p)
        self.assertEqual([o for o, _ in rows], [1, 2, 3])
        self.assertNotIn("main character", rows[0][1])
        self.assertIn("move", rows[0][1])
        self.assertTrue(self.hv.prompts_txt(self.p, numbered=True).startswith("001 | "))
