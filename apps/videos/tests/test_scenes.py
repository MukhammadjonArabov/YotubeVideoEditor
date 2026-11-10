import io

from django.test import TestCase
from django.urls import reverse
from PIL import Image

from apps.videos.models import Project, Scene
from apps.videos.services import scenes as ops
from apps.videos.services.images import normalize_to_1080p


def orders(project):
    return list(project.scenes.order_by("order").values_list("narration", flat=True))


class SceneOpsTests(TestCase):
    def setUp(self):
        self.p = Project.objects.create(topic="Test topic")
        for t in "ABC":
            ops.add_scene(self.p, narration=t)

    def test_add_at_end_and_after(self):
        self.assertEqual(orders(self.p), ["A", "B", "C"])
        ops.add_scene(self.p, after_order=1, narration="X")
        self.assertEqual(orders(self.p), ["A", "X", "B", "C"])
        self.assertEqual(list(self.p.scenes.values_list("order", flat=True)), [1, 2, 3, 4])
        ops.add_scene(self.p, after_order=0, narration="Z")
        self.assertEqual(orders(self.p)[0], "Z")

    def test_move(self):
        b = self.p.scenes.get(narration="B")
        self.assertTrue(ops.move_scene(b, -1))
        self.assertEqual(orders(self.p), ["B", "A", "C"])
        c = self.p.scenes.get(narration="C")
        self.assertFalse(ops.move_scene(c, +1))

    def test_delete_renumbers(self):
        ops.delete_scene(self.p.scenes.get(narration="A"))
        self.assertEqual(list(self.p.scenes.values_list("order", "narration")), [(1, "B"), (2, "C")])
        self.p.refresh_from_db()
        self.assertTrue(self.p.has_unrendered_changes)

    def test_edit_narration_invalidates_audio(self):
        s = self.p.scenes.get(narration="A")
        s.audio_duration, s.clip_hash, s.status = 3.2, "abc", Scene.Status.READY
        s.save()
        s.narration = "A2"
        ops.apply_scene_edit(s, {"narration"})
        s.refresh_from_db()
        self.assertIsNone(s.audio_duration)
        self.assertEqual(s.clip_hash, "")
        self.assertEqual(s.status, Scene.Status.PENDING)


class ImageNormalizeTests(TestCase):
    def test_any_size_becomes_1080p(self):
        for size in [(800, 800), (4000, 1000), (1280, 720)]:
            buf = io.BytesIO()
            Image.new("RGB", size, "red").save(buf, "JPEG")
            for mode in ("crop", "letterbox"):
                out = Image.open(io.BytesIO(normalize_to_1080p(buf.getvalue(), mode)))
                self.assertEqual(out.size, (1920, 1080))


class SceneViewTests(TestCase):
    def setUp(self):
        self.p = Project.objects.create(topic="Views topic")
        self.s = ops.add_scene(self.p, narration="Hello")




