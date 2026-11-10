import json
import subprocess
import tempfile
from io import StringIO
from pathlib import Path
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from apps.videos import music_tasks
from apps.videos.models import MusicClip, MusicVideo, Niche
from apps.videos.services import media_library, music_qc, render
from apps.videos.services import music_video as mvs

TMP = tempfile.mkdtemp(prefix="musictest_")


def tone(path: Path, seconds: float, freq: int = 330, volume: float = 0.15) -> bytes:
    subprocess.run([render.ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                    f"sine=frequency={freq}:duration={seconds}", "-af", f"volume={volume}", "-ar", "44100", str(path)], check=True)
    return path.read_bytes()


def clip(path: Path, seconds: float = 4, colour="blue") -> bytes:
    subprocess.run([render.ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                    f"color=c={colour}:s=640x360:r=24:d={seconds}", "-pix_fmt", "yuv420p", str(path)], check=True)
    return path.read_bytes()


def music_niche() -> Niche:
    return Niche.objects.create(name="Musiqa", slug="musiqa", kind="music", emoji="🎵", is_active=False)


class PlanTests(TestCase):
    def test_ctas_start_early_then_every_few_minutes_and_stay_clear_of_the_end(self):
        plan = mvs.plan_ctas(30 * 60, 5)
        subs = [t for t, k in plan if k == "subscribe"]
        likes = [t for t, k in plan if k == "like"]
        self.assertEqual(subs[0], 45)
        self.assertEqual([round(b - a) for a, b in zip(subs, subs[1:])], [300] * (len(subs) - 1))
        self.assertTrue(all(l - s == mvs.CTA_GAP for s, l in zip(subs, likes)))
        self.assertLess(max(t for t, _ in plan), 30 * 60 - mvs.END_MARGIN)
        self.assertEqual(mvs.plan_ctas(30, 5), [])
        self.assertEqual(mvs.plan_ctas(600, 5, False, False), [])

    def test_loop_plan_counts_passes(self):
        plan = mvs.loop_plan(210, 1800)
        self.assertEqual(plan["target_min"], 30.0)
        self.assertGreaterEqual(plan["passes"] * (210 - plan["crossfade"]) + plan["crossfade"], 1800)

    def test_prompt_always_carries_a_vocal_clause(self):
        self.assertIn("female", mvs.build_prompt("calm river", True))
        self.assertIn("Instrumental", mvs.build_prompt("calm river", False))


class CommandTests(TestCase):
    def test_audio_loop_chain_and_seamless_block(self):
        cmd = mvs.audio_loop_cmd("ffmpeg", Path("m.mp3"), 300, 1800, Path("o.m4a"))
        fc = cmd[cmd.index("-filter_complex") + 1]
        self.assertEqual(fc.count("acrossfade"), cmd.count("-i") - 1)
        self.assertIn("loudnorm", fc)
        c, length = mvs.block_cmd("ffmpeg", [Path("a.mp4"), Path("b.mp4")], [20.0, 20.0], Path("b.mp4"))
        self.assertEqual(c.count("-i"), 3)
        self.assertAlmostEqual(length, 38.0)

    def test_compose_music_needs_a_paid_plan_and_reports_it(self):
        paid = mock.Mock(status_code=402, content=b"x")
        paid.json.return_value = {"detail": {"message": "Music API is not available for free users."}}
        with override_settings(ELEVENLABS_API_KEY="k"), mock.patch("requests.post", return_value=paid), \
                self.assertRaisesRegex(mvs.MusicError, "pullik"):
            mvs.compose_music("calm", 120)
        ok = mock.Mock(status_code=200, content=b"x" * 20000)
        with override_settings(ELEVENLABS_API_KEY="k"), mock.patch("requests.post", return_value=ok) as post:
            self.assertEqual(len(mvs.compose_music("calm", 999, vocals=False)), 20000)
        body = post.call_args.kwargs["json"]
        self.assertEqual((body["music_length_ms"], body["force_instrumental"]), (300000, True))


@override_settings(MEDIA_ROOT=TMP)
class QualityTests(TestCase):
    def setUp(self):
        Path(TMP).mkdir(parents=True, exist_ok=True)

    def test_steady_track_scores_well_and_silence_gap_is_caught(self):
        d = Path(TMP)
        tone(d / "good.wav", 160)
        good = music_qc.analyze(d / "good.wav")
        self.assertGreaterEqual(good["score"], 85, good["issues"])
        # same tone with a 4 s hole in the middle
        subprocess.run([render.ffmpeg_exe(), "-y", "-loglevel", "error", "-i", str(d / "good.wav"), "-af",
                        "volume=enable='between(t,70,74)':volume=0", str(d / "bad.wav")], check=True)
        bad = music_qc.analyze(d / "bad.wav")
        self.assertTrue(bad["metrics"]["silences"])
        self.assertTrue(any(i["level"] == "bad" for i in bad["issues"]))
        self.assertLess(bad["score"], good["score"])
        self.assertIn("Qoniqarsiz", bad["verdict"])

    def test_too_loud_and_short_tracks_are_flagged(self):
        d = Path(TMP)
        tone(d / "loud.wav", 30, volume=6)
        rep = music_qc.analyze(d / "loud.wav")
        texts = " ".join(i["text"] for i in rep["issues"])
        self.assertIn("Uzunligi", texts)
        self.assertTrue(any(i["level"] == "bad" for i in rep["issues"]), rep)


@override_settings(MEDIA_ROOT=TMP)
class EndToEndTests(TestCase):
    def test_real_render_loops_music_and_clips_to_the_target_length(self):
        d = Path(TMP)
        d.mkdir(parents=True, exist_ok=True)
        mv = MusicVideo.objects.create(title="T", target_minutes=1)
        mvs.save_music(mv, tone(d / "m.mp3", 12), "m.mp3")
        mv.refresh_from_db()
        self.assertTrue(mv.music_file)
        self.assertEqual(mv.takes.count(), 1)
        self.assertTrue(mv.takes.get().is_selected)
        for i, col in enumerate(("blue", "green"), start=1):
            c = MusicClip(video=mv, order=i)
            c.file.save(f"c{i}.mp4", SimpleUploadedFile(f"c{i}.mp4", clip(d / f"c{i}.mp4", 5, col)), save=False)
            c.duration = 5
            c.save()
        out, total = mvs.render_music_video(mv, target_sec=25)
        self.assertAlmostEqual(media_library.audio_duration(out), 25, delta=1.0)
        probe = subprocess.run([render.ffmpeg_exe(), "-hide_banner", "-i", str(out)], capture_output=True, text=True).stderr
        self.assertIn("1920x1080", probe)
        self.assertIn("Audio: aac", probe)

    def test_task_marks_a_failed_render_and_frees_the_video(self):
        mv = MusicVideo.objects.create(title="Empty")
        music_tasks.render_video(mv.pk)
        mv.refresh_from_db()
        self.assertEqual((mv.status, mv.is_working), (MusicVideo.Status.FAILED, False))

    def test_generate_takes_saves_checked_takes_and_reports_a_paywall(self):
        d = Path(TMP)
        d.mkdir(parents=True, exist_ok=True)
        mv = MusicVideo.objects.create(title="G", music_prompt="calm", music_seconds=60)
        data = tone(d / "g.mp3", 160)
        with mock.patch.object(mvs, "compose_music", return_value=data):
            music_tasks.generate_takes(mv.pk, 2)
        mv.refresh_from_db()
        self.assertEqual(mv.takes.count(), 2)
        self.assertEqual(mv.takes.filter(is_selected=True).count(), 1)
        self.assertFalse(mv.is_working)
        self.assertTrue(all(t.score for t in mv.takes.all()))
        with mock.patch.object(mvs, "compose_music", side_effect=mvs.MusicError("pullik reja")):
            music_tasks.generate_takes(mv.pk, 1)
        mv.refresh_from_db()
        self.assertIn("pullik", mv.error_message)
        self.assertFalse(mv.is_working)


@override_settings(MEDIA_ROOT=TMP)
class ViewTests(TestCase):
    def test_niche_page_detail_flow_edit_takes_and_limits(self):
        niche = music_niche()
        self.assertContains(self.client.get("/"), "Musiqa")
        self.assertEqual(self.client.get("/yonalish/musiqa/").status_code, 200)
        r = self.client.post("/musiqa/yangi/", {"title": "Rain"})
        mv = MusicVideo.objects.get()
        self.assertEqual((r.status_code, mv.niche_id), (302, niche.pk))
        page = self.client.get(f"/musiqa/{mv.pk}/")
        self.assertContains(page, "Yaratish (ElevenLabs)")
        self.assertContains(page, "Flow video promptlari")
        # settings
        self.client.post(f"/musiqa/{mv.pk}/saqlash/", {"title": "Rain", "music_prompt": "rain", "music_seconds": "9999",
                                                       "target_minutes": "25", "cta_every_min": "4"})
        mv.refresh_from_db()
        self.assertEqual((mv.music_seconds, mv.target_minutes, mv.vocals, mv.add_like), (300, 25, False, False))
        # editable Flow prompts: empty ones disappear, a new one is appended
        self.client.post(f"/musiqa/{mv.pk}/flow/", {"flow1": "first prompt", "flowtitle1": "A", "flow2": "", "flow_new": "third"})
        mv.refresh_from_db()
        self.assertEqual([f["prompt"] for f in mv.flow_prompts], ["first prompt", "third"])
        d = Path(TMP)
        d.mkdir(parents=True, exist_ok=True)
        for i in range(8):  # more than the limit is refused
            self.client.post(f"/musiqa/{mv.pk}/klip/", {"clips": SimpleUploadedFile(f"c{i}.mp4", clip(d / f"v{i}.mp4", 2))})
        self.assertEqual(mv.clips.count(), 6)
        # two uploaded takes: the first is selected, the second can be chosen, deleting the chosen one promotes the other
        for i, f in enumerate((330, 440)):
            self.client.post(f"/musiqa/{mv.pk}/yuklash/", {"audio": SimpleUploadedFile("m.wav", tone(d / f"t{i}.wav", 160, f))})
        first, second = mv.takes.order_by("created_at")
        self.assertTrue(first.is_selected and not second.is_selected)
        self.client.post(f"/musiqa/variant/{second.pk}/tanlash/")
        second.refresh_from_db()
        self.assertTrue(second.is_selected)
        page = self.client.get(f"/musiqa/{mv.pk}/")
        self.assertContains(page, "Sifat:")
        self.client.post(f"/musiqa/variant/{second.pk}/ochirish/")
        first.refresh_from_db()
        self.assertTrue(first.is_selected)
        # loop-join preview
        self.client.post(f"/musiqa/{mv.pk}/ulanish/")
        self.assertTrue((Path(TMP) / "music" / f"m{mv.pk}" / "loop_preview.mp3").exists())
        # render is queued, not run, in the view
        with mock.patch.object(music_tasks, "async_task") as q:
            self.client.post(f"/musiqa/{mv.pk}/montaj/")
        q.assert_called_once()
        self.client.post(f"/musiqa/{mv.pk}/ochirish/")
        self.assertFalse(MusicVideo.objects.exists())


class ManagementCommandTests(TestCase):
    def spec(self, **over) -> dict:
        s = {"title": "Rain Forest Lullaby", "music_prompt": "Soft wordless female vocalise over a flowing stream",
             "flow_prompts": [{"title": "Stream", "prompt": " ".join(["a calm forest stream with moss and soft light"] * 5)},
                              {"title": "Lake", "prompt": " ".join(["a misty lake at dawn with gentle ripples"] * 5)}],
             "titles": ["Calm Forest Stream for DEEP Sleep"], "description": "d", "tags": ["sleep music"],
             "thumbnail_prompts": [{"text": "SLEEP", "prompt": "p"}]}
        s.update(over)
        return s

    def run_cmd(self, spec: dict, *extra) -> str:
        path = Path(tempfile.mkdtemp(prefix="musicspec_")) / "s.json"
        path.write_text(json.dumps(spec), encoding="utf-8")
        out = StringIO()
        call_command("music_new", str(path), *extra, stdout=out)
        return out.getvalue()

    def test_music_new_creates_niche_project_and_kit_then_updates(self):
        out = self.run_cmd(self.spec())
        mv = MusicVideo.objects.get()
        self.assertIn(f"/musiqa/{mv.pk}/", out)
        self.assertEqual((mv.niche.kind, mv.niche.is_active), ("music", False))
        self.assertEqual(len(mv.flow_prompts), 2)
        self.assertEqual(mv.kit["titles"], ["Calm Forest Stream for DEEP Sleep"])
        self.run_cmd(self.spec(title="Changed"), "--project", str(mv.pk))
        mv.refresh_from_db()
        self.assertEqual((MusicVideo.objects.count(), Niche.objects.filter(kind="music").count(), mv.title), (1, 1, "Changed"))

    def test_music_new_rejects_bad_specs(self):
        with self.assertRaisesRegex(CommandError, "Flow"):
            self.run_cmd(self.spec(flow_prompts=[{"title": "x", "prompt": "short"}]))
        with self.assertRaisesRegex(CommandError, "artist"):
            self.run_cmd(self.spec(music_prompt="in the style of a famous artist"))
