import subprocess
import tempfile
from pathlib import Path
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from apps.videos import music_tasks
from apps.videos.models import MusicClip, MusicVideo
from apps.videos.services import media_library, render
from apps.videos.services import music_video as mvs

TMP = tempfile.mkdtemp(prefix="musictest_")


def tone(path: Path, seconds: float) -> bytes:
    subprocess.run([render.ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                    f"sine=frequency=330:duration={seconds}", "-ar", "44100", str(path)], check=True)
    return path.read_bytes()


def clip(path: Path, seconds: float = 4, colour="blue") -> bytes:
    subprocess.run([render.ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                    f"color=c={colour}:s=640x360:r=24:d={seconds}", "-pix_fmt", "yuv420p", str(path)], check=True)
    return path.read_bytes()


class PlanTests(TestCase):
    def test_ctas_start_early_then_every_few_minutes_and_stay_clear_of_the_end(self):
        plan = mvs.plan_ctas(30 * 60, 5)
        subs = [t for t, k in plan if k == "subscribe"]
        likes = [t for t, k in plan if k == "like"]
        self.assertEqual(subs[0], 45)
        self.assertEqual([round(b - a) for a, b in zip(subs, subs[1:])], [300] * (len(subs) - 1))
        self.assertTrue(all(l - s == mvs.CTA_GAP for s, l in zip(subs, likes)))
        self.assertLess(max(t for t, _ in plan), 30 * 60 - mvs.END_MARGIN)
        self.assertEqual([k for _, k in mvs.plan_ctas(600, 5, subscribe=False)], ["like"] * 2)
        self.assertEqual(mvs.plan_ctas(30, 5), [])  # too short
        self.assertEqual(mvs.plan_ctas(600, 5, False, False), [])

    def test_ass_has_both_animations(self):
        text = mvs.cta_ass([(45.0, "subscribe"), (47.0, "like")])
        self.assertIn("SUBSCRIBE", text)
        self.assertIn("LIKED", text)
        self.assertIn("Dialogue", text)


class CommandTests(TestCase):
    def test_audio_loop_chain_and_seamless_block(self):
        cmd = mvs.audio_loop_cmd("ffmpeg", Path("m.mp3"), 300, 1800, Path("o.m4a"))
        self.assertEqual(cmd.count("-i"), 7)  # 300 s track, 1800 s target, 4 s joins -> 7 copies
        fc = cmd[cmd.index("-filter_complex") + 1]
        self.assertEqual(fc.count("acrossfade"), 6)
        self.assertIn("atrim=0:1800.00", fc)
        c, length = mvs.block_cmd("ffmpeg", [Path("a.mp4"), Path("b.mp4")], [20.0, 20.0], Path("b.mp4"))
        self.assertEqual(c.count("-i"), 3)  # a, b and a again: the end flows into the start
        self.assertAlmostEqual(length, 38.0)  # 40 s of clips minus two 1 s cross-fades
        one, length1 = mvs.block_cmd("ffmpeg", [Path("a.mp4")], [20.0], Path("b.mp4"))
        self.assertAlmostEqual(length1, 19.0)
        f = mvs.final_cmd("ffmpeg", Path("b.mp4"), Path("a.m4a"), "cta.ass", 1800, Path("f.mp4"))
        self.assertIn("-stream_loop", f)
        self.assertEqual(f[f.index("-vf") + 1], "ass=cta.ass")

    def test_compose_music_needs_a_paid_plan_and_reports_it(self):
        paid = mock.Mock(status_code=402, content=b"x")
        paid.json.return_value = {"detail": {"message": "Music API is not available for free users."}}
        with override_settings(ELEVENLABS_API_KEY="k"), mock.patch("requests.post", return_value=paid), \
                self.assertRaisesRegex(mvs.MusicError, "pullik"):
            mvs.compose_music("calm", 6)
        ok = mock.Mock(status_code=200, content=b"x" * 20000)
        with override_settings(ELEVENLABS_API_KEY="k"), mock.patch("requests.post", return_value=ok) as post:
            self.assertEqual(len(mvs.compose_music("calm", 99)), 20000)
        body = post.call_args.kwargs["json"]
        self.assertEqual((body["music_length_ms"], body["force_instrumental"]), (600000, True))  # capped at 10 minutes


@override_settings(MEDIA_ROOT=TMP)
class EndToEndTests(TestCase):
    def test_real_render_loops_music_and_clips_to_the_target_length(self):
        d = Path(TMP)
        d.mkdir(parents=True, exist_ok=True)
        mv = MusicVideo.objects.create(title="T", target_minutes=1)
        mvs.save_music(mv, tone(d / "m.mp3", 12), "m.mp3")
        for i, col in enumerate(("blue", "green"), start=1):
            c = MusicClip(video=mv, order=i)
            c.file.save(f"c{i}.mp4", SimpleUploadedFile(f"c{i}.mp4", clip(d / f"c{i}.mp4", 5, col)), save=False)
            c.duration = 5
            c.save()
        out, total = mvs.render_music_video(mv, target_sec=25)
        self.assertAlmostEqual(media_library.audio_duration(out), 25, delta=1.0)  # 12 s track looped past 2x, clips 5 s
        probe = subprocess.run([render.ffmpeg_exe(), "-hide_banner", "-i", str(out)], capture_output=True, text=True).stderr
        self.assertIn("1920x1080", probe)
        self.assertIn("Audio: aac", probe)

    def test_task_marks_a_failed_render_and_frees_the_video(self):
        mv = MusicVideo.objects.create(title="Empty")
        music_tasks.render_video(mv.pk)
        mv.refresh_from_db()
        self.assertEqual((mv.status, mv.is_working), (MusicVideo.Status.FAILED, False))
        self.assertIn("musiqa", mv.error_message.lower())


@override_settings(MEDIA_ROOT=TMP)
class ViewTests(TestCase):
    def test_pages_create_upload_and_limits(self):
        self.assertEqual(self.client.get("/musiqa/").status_code, 200)
        r = self.client.post("/musiqa/yangi/", {"title": "Rain"})
        mv = MusicVideo.objects.get()
        self.assertEqual(r.status_code, 302)
        page = self.client.get(f"/musiqa/{mv.pk}/")
        self.assertContains(page, "Musiqa yaratish (ElevenLabs)")
        self.assertContains(page, "Flow")
        d = Path(TMP)
        d.mkdir(parents=True, exist_ok=True)
        for i in range(5):  # a fifth clip is refused
            self.client.post(f"/musiqa/{mv.pk}/klip-yuklash/",
                             {"clips": SimpleUploadedFile(f"c{i}.mp4", clip(d / f"v{i}.mp4", 2))})
        self.assertEqual(mv.clips.count(), 4)
        self.client.post(f"/musiqa/{mv.pk}/musiqa-yuklash/", {"audio": SimpleUploadedFile("m.mp3", tone(d / "t.mp3", 9))})
        mv.refresh_from_db()
        self.assertAlmostEqual(mv.music_duration, 9, delta=1)
        self.assertEqual(mv.status, MusicVideo.Status.MUSIC_READY)
        self.client.post(f"/musiqa/{mv.pk}/saqlash/", {"title": "Rain", "music_minutes": "99", "target_minutes": "25",
                                                       "cta_every_min": "4", "add_like": "on"})
        mv.refresh_from_db()
        self.assertEqual((mv.music_minutes, mv.target_minutes, mv.cta_every_min, mv.add_subscribe, mv.add_like),
                         (10, 25, 4, False, True))
        with mock.patch("apps.videos.music_tasks.async_task") as q:
            self.client.post(f"/musiqa/{mv.pk}/montaj/")
        q.assert_called_once()
        self.assertTrue(MusicVideo.objects.get(pk=mv.pk).is_working)
