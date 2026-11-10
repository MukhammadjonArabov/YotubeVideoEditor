import io
import subprocess
import tempfile
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from apps.videos.models import FlowJob, Project
from apps.videos.services import flow_queue, render
from apps.videos.services import scenes as ops

TMP_MEDIA = tempfile.mkdtemp(prefix="flowtest_")


def png_bytes(colour="red"):
    buf = io.BytesIO()
    Image.new("RGB", (1280, 720), colour).save(buf, "PNG")
    return buf.getvalue()


def make_video(path: Path, seconds=3, black=False):
    src = (f"color=c=black:s=320x180:r=24:d={seconds}" if black
           else f"testsrc=size=320x180:rate=24:duration={seconds}")
    subprocess.run([render.ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "lavfi", "-i", src,
                    "-pix_fmt", "yuv420p", str(path)], check=True)
    return path.read_bytes()


@override_settings(MEDIA_ROOT=TMP_MEDIA, FLOW_API_TOKEN="secret-token", FLOW_MAX_ATTEMPTS=2)
class FlowQueueTests(TestCase):
    def setUp(self):
        self.p = Project.objects.create(topic="Flow queue", style_guide="STYLE")
        for i in range(1, 5):
            s = ops.add_scene(self.p, narration=f"n{i}", image_prompt="a skull on a rock")
            s.beat_type = "hook" if i <= 2 else "normal"
            s.save(update_fields=["beat_type"])

    def test_enqueue_images_then_only_hook_videos_with_pictures(self):
        self.assertEqual(flow_queue.enqueue(self.p, "image"), 4)
        self.assertEqual(flow_queue.enqueue(self.p, "image"), 0)  # already queued
        self.assertEqual(flow_queue.enqueue(self.p, "video"), 0)  # hook pictures do not exist yet
        job = flow_queue.claim_next()
        self.assertEqual((job.kind, job.scene.order, job.status, job.attempts), ("image", 1, "running", 1))
        self.assertIn("Style:", job.prompt)

    def test_image_result_is_saved_on_the_scene(self):
        flow_queue.enqueue(self.p, "image")
        job = flow_queue.claim_next()
        job = flow_queue.complete(job, png_bytes(), "scene_1.png")
        self.assertEqual(job.status, "done")
        scene = self.p.scenes.get(order=1)
        self.assertTrue(scene.image)
        self.assertTrue(scene.image_locked)

    def test_video_flow_end_to_end_and_bad_clips_are_retried(self):
        scene = self.p.scenes.get(order=1)
        from apps.videos.services import manual_images

        manual_images.save_uploaded(scene, png_bytes())
        self.assertEqual(flow_queue.enqueue(self.p, "video"), 1)
        job = flow_queue.claim_next()
        self.assertEqual(flow_queue.start_frame(job)[:4], b"\x89PNG")
        d = Path(TMP_MEDIA)
        d.mkdir(parents=True, exist_ok=True)
        # a black clip is rejected and goes back to the queue ...
        job = flow_queue.complete(job, make_video(d / "black.mp4", black=True), "scene_1.mp4")
        self.assertEqual((job.status, "qora" in job.note), ("pending", True))
        # ... the second try is a real moving clip
        job = flow_queue.claim_next()
        job = flow_queue.complete(job, make_video(d / "ok.mp4"), "scene_1.mp4")
        self.assertEqual(job.status, "done", job.note)
        self.assertTrue(self.p.scenes.get(order=1).video)

    def test_after_max_attempts_a_bad_result_waits_for_a_human(self):
        flow_queue.enqueue(self.p, "image")
        job = flow_queue.claim_next()
        flow_queue.fail(job, "Flow refused")
        job.refresh_from_db()
        self.assertEqual((job.status, job.attempts), ("pending", 1))
        job = flow_queue.claim_next()
        flow_queue.fail(job, "Flow refused again")
        job.refresh_from_db()
        self.assertEqual(job.status, "failed")
        flow_queue.retry(job)
        job.refresh_from_db()
        self.assertEqual((job.status, job.attempts), ("pending", 0))

    def test_stale_running_jobs_come_back(self):
        flow_queue.enqueue(self.p, "image")
        job = flow_queue.claim_next()
        FlowJob.objects.filter(pk=job.pk).update(claimed_at=job.claimed_at.replace(year=2020))
        self.assertEqual(flow_queue.release_stale(), 1)


@override_settings(MEDIA_ROOT=TMP_MEDIA, FLOW_API_TOKEN="secret-token")
class FlowApiTests(TestCase):
    def setUp(self):
        self.p = Project.objects.create(topic="Flow api")
        ops.add_scene(self.p, narration="n1", image_prompt="a campfire")
        flow_queue.enqueue(self.p, "image")
        self.h = {"HTTP_X_FLOW_TOKEN": "secret-token"}

    def test_token_required(self):
        self.assertEqual(self.client.get("/api/flow/next/").status_code, 401)
        self.assertEqual(self.client.get("/api/flow/next/", HTTP_X_FLOW_TOKEN="nope").status_code, 401)

    def test_next_result_roundtrip(self):
        r = self.client.get("/api/flow/next/", **self.h).json()
        job = r["job"]
        self.assertEqual((job["kind"], job["scene"], job["frame"]), ("image", 1, False))
        up = SimpleUploadedFile("scene_1.png", png_bytes(), content_type="image/png")
        res = self.client.post(f"/api/flow/job/{job['id']}/result/", {"file": up}, **self.h)
        self.assertEqual(res.json()["status"], "done")
        self.assertIsNone(self.client.get("/api/flow/next/", **self.h).json()["job"])

    def test_fail_endpoint(self):
        job = self.client.get("/api/flow/next/", **self.h).json()["job"]
        res = self.client.post(f"/api/flow/job/{job['id']}/fail/", data='{"error": "no prompt box"}',
                               content_type="application/json", **self.h)
        self.assertEqual(res.json()["status"], "pending")  # first failure -> one more try

    def test_prompts_page_and_project_page_show_spaced_prompts(self):
        r = self.client.get(f"/videolar/{self.p.pk}/promptlar/")
        self.assertContains(r, 'id="all-prompts"')
        self.assertNotContains(r, "secret-token")  # the extension card is gone
        r = self.client.get(f"/videolar/{self.p.pk}/")
        self.assertContains(r, "Rasm promptlari")
        self.assertContains(r, 'id="prompts-box"')


@override_settings(MEDIA_ROOT=TMP_MEDIA, FLOW_API_TOKEN="secret-token", FLOW_MAX_ATTEMPTS=2)
class FlowExportTests(TestCase):
    def test_results_are_saved_under_scene_numbered_names_and_video_for_all_scenes(self):
        p = Project.objects.create(topic="Flow export")
        for i in range(1, 4):
            s = ops.add_scene(p, narration=f"n{i}", image_prompt="a skull on a rock")
            s.beat_type = "hook" if i == 1 else "normal"
            s.save(update_fields=["beat_type"])
        flow_queue.enqueue(p, "image")
        for _ in range(3):
            job = flow_queue.claim_next()
            flow_queue.complete(job, png_bytes(), f"x{job.scene.order}.png")
        folder = flow_queue.export_dir(p)
        self.assertEqual(sorted(f.name for f in folder.iterdir()),
                         ["scene_001_image.png", "scene_002_image.png", "scene_003_image.png"])
        self.assertEqual(flow_queue.enqueue(p, "video"), 1)  # hook only by default
        self.assertEqual(flow_queue.enqueue(p, "video", hook_only=False), 2)  # the other two scenes, 1 already queued
        job = flow_queue.claim_next()
        d = Path(TMP_MEDIA)
        d.mkdir(parents=True, exist_ok=True)
        flow_queue.complete(job, make_video(d / "e.mp4"), "whatever.mp4")
        self.assertTrue((folder / f"scene_{job.scene.order:03d}_video.mp4").exists())


@override_settings(MEDIA_ROOT=TMP_MEDIA, FLOW_API_TOKEN="secret-token", FLOW_MAX_ATTEMPTS=2)
class FlowAutoRenderTests(TestCase):
    def setUp(self):
        self.p = Project.objects.create(topic="Auto render", status=Project.Status.APPROVED, flow_auto_render=True)
        for i in range(1, 3):
            ops.add_scene(self.p, narration=f"n{i}", image_prompt="a campfire")
        flow_queue.enqueue(self.p, "image")

    def test_montage_starts_once_when_the_last_flow_job_is_done(self):
        from unittest import mock

        with mock.patch("apps.videos.tasks.enqueue") as enq:
            flow_queue.complete(flow_queue.claim_next(), png_bytes(), "a.png")
            enq.assert_not_called()  # one job still open
            flow_queue.complete(flow_queue.claim_next(), png_bytes(), "b.png")
            enq.assert_called_once()
            self.assertEqual(enq.call_args.args[0], "produce_video")
        self.p.refresh_from_db()
        self.assertFalse(self.p.flow_auto_render)  # one-shot

    def test_not_started_when_not_asked_or_not_approved(self):
        from unittest import mock

        Project.objects.filter(pk=self.p.pk).update(flow_auto_render=False)
        with mock.patch("apps.videos.tasks.enqueue") as enq:
            for _ in range(2):
                flow_queue.complete(flow_queue.claim_next(), png_bytes(), "a.png")
            enq.assert_not_called()

    def test_normal_image_step_leaves_scenes_waiting_for_flow_alone(self):
        waiting = flow_queue.scenes_waiting_for_flow(self.p)
        self.assertEqual(len(waiting), 2)
