import tempfile
import threading
from pathlib import Path

from django.test import TestCase, override_settings

from apps.videos.models import Project
from apps.videos.services import assets
from apps.videos.services.image_providers import ImageProviderError
from apps.videos.services.tts import TTSResult

TINY_PNG = None


def png_bytes():
    import io

    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", (64, 64), (200, 100, 50)).save(buf, "PNG")
    return buf.getvalue()


class FakeImages:
    name = "fake"
    supports_reference = False

    def __init__(self, fail_after=None):
        self.calls = 0
        self.lock = threading.Lock()
        self.fail_after = fail_after
        self.threads = set()

    def generate(self, prompt, seed=None, references=None):
        with self.lock:
            self.calls += 1
            n = self.calls
            self.threads.add(threading.get_ident())
        if self.fail_after is not None and n > self.fail_after:
            raise ImageProviderError("Cloudflare kunlik bepul limiti tugadi")
        return png_bytes()


class FakeVoice:
    name = "fakevoice"
    extension = ".mp3"

    def synthesize(self, text, out_path):
        out = Path(out_path)
        out.write_bytes(b"ID3fake")
        return TTSResult(out, 1.5, None)


@override_settings(IMAGE_CONCURRENCY=2, TTS_CONCURRENCY=2, CLOUDFLARE_ACCOUNT_ID="", GEMINI_API_KEY="")
class ParallelAssetTests(TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self.tmp.name)
        self.override.enable()
        self.p = Project.objects.create(topic="Parallel")
        for i in range(1, 7):
            self.p.scenes.create(order=i, narration=f"Scene {i} words", image_prompt="a cave at night")

    def tearDown(self):
        self.override.disable()
        self.tmp.cleanup()

    def test_images_and_voice_together(self):
        scenes = list(self.p.scenes.order_by("order"))
        imgs = FakeImages()
        rep = assets.produce(scenes, scenes, imgs, FakeVoice(), qa=False)
        self.assertEqual(rep.images_done, 6)
        self.assertEqual(rep.voice_failed, [])
        for s in self.p.scenes.all():
            self.assertTrue(s.image and s.audio)
            self.assertEqual(s.audio_duration, 1.5)

    def test_quota_stops_remaining_images_and_keeps_error(self):
        scenes = list(self.p.scenes.order_by("order"))
        with override_settings(IMAGE_CONCURRENCY=1):
            rep = assets.produce(scenes, scenes, FakeImages(fail_after=2), FakeVoice(), qa=False)
        self.assertTrue(rep.image_quota_hit)
        self.assertEqual(rep.images_done, 2)
        self.assertEqual(rep.images_failed + rep.images_skipped, 4)
        failed = self.p.scenes.filter(status="failed")
        self.assertEqual(failed.count(), 1)  # the scene that hit the limit keeps its error despite its new voice
        self.assertTrue(all(s.audio for s in self.p.scenes.all()))


class MissingFileTests(TestCase):
    def test_a_scene_whose_voice_file_vanished_needs_its_voice_again(self):
        from apps.videos.models import Project
        from apps.videos.services.voice import needs_audio

        p = Project.objects.create(topic="Missing file")
        s = p.scenes.create(order=1, narration="Hello there.")
        self.assertTrue(needs_audio(s))
        s.audio = "projects/pX/audio/does_not_exist.mp3"
        self.assertTrue(needs_audio(s))  # named in the database, gone from the disk
