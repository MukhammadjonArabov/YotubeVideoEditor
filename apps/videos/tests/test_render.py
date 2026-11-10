import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest import mock

from django.test import TestCase, override_settings

from apps.videos import tasks
from apps.videos.models import Niche, Project
from apps.videos.services import media_library, render, subtitles
from apps.videos.services.tts import TTSResult, WordTiming
from apps.videos.services.tts.elevenlabs import words_from_alignment

TMP_MEDIA = tempfile.mkdtemp(prefix="ae-render-")


def tearDownModule():
    shutil.rmtree(TMP_MEDIA, ignore_errors=True)


class CommandBuilderTests(TestCase):
    def spec(self, **kw):
        base = dict(image=Path("img.png"), audio=Path("a.mp3"), out=Path("out.mp4"), duration=4.4, motion="zoom_in",
                    size=(1920, 1080), prescale=1.5, codec_args=["-c:v", "libx264", "-preset", "veryfast", "-crf", "21"])
        base.update(kw)
        return render.ClipSpec(**base)

    def test_motion_rotation(self):
        self.assertEqual([render.motion_for(i) for i in range(6)],
                         ["zoom_in", "pan_right", "zoom_out", "pan_left", "diagonal", "zoom_in"])

    def test_zoompan_expressions(self):
        ease = "(0.5-0.5*cos(PI*on/132))"
        self.assertEqual(render.zoompan_expr("zoom_in", 133)[0], f"1+0.12*{ease}")
        self.assertEqual(render.zoompan_expr("zoom_out", 133)[0], f"1.12-0.12*{ease}")
        self.assertEqual(render.zoompan_expr("pan_left", 11)[1], "(iw-iw/zoom)*(1-(0.5-0.5*cos(PI*on/10)))")
        self.assertEqual(render.zoompan_expr("anything", 11, hook=True)[0], "1+0.22*(1-pow(1-on/10,2))")
        # offset past the end = frozen final frame (progress clamped at 1)
        self.assertIn("min((on+10)/10,1)", render.zoompan_expr("zoom_in", 11, offset=10)[0])

    def test_scene_clip_cmd(self):
        hit = render.SfxHit(Path("w.wav"), 0.35, 0.2)
        cmd = render.scene_clip_cmd("ffmpeg", self.spec(sfx=[hit], subtitles="subs_final_001.ass"))
        fc = cmd[cmd.index("-filter_complex") + 1]
        self.assertIn("scale=2880:1620", fc)
        self.assertIn("zoompan=z='1+0.12*(0.5-0.5*cos(PI*on/131))'", fc)
        self.assertIn("d=132:s=1920x1080:fps=30", fc)
        self.assertIn("ass=subs_final_001.ass[v]", fc)
        self.assertIn("apad=whole_dur=4.400", fc)
        self.assertIn("acompressor", fc)
        self.assertIn("volume=0.35,adelay=200|200[fx0]", fc)
        self.assertIn("[voice][fx0]amix=inputs=2:duration=first:normalize=0", fc)
        self.assertEqual(cmd[cmd.index("-t") + 1], "4.400")
        self.assertIn("libx264", cmd)
        self.assertEqual(cmd[cmd.index("-c:a") + 1], "pcm_s16le")
        self.assertNotIn("xfade", fc)
        no_extra = render.scene_clip_cmd("ffmpeg", self.spec())
        self.assertNotIn("w.wav", no_extra)
        self.assertIn("[voice]alimiter", no_extra[no_extra.index("-filter_complex") + 1])

    def test_transition_and_fades(self):
        spec = self.spec(transition="smoothleft", prev_image=Path("prev.png"), prev_motion="pan_right", prev_frames=90,
                         fade_out=True)
        cmd = render.scene_clip_cmd("ffmpeg", spec)
        fc = cmd[cmd.index("-filter_complex") + 1]
        self.assertIn("prev.png", cmd)
        self.assertIn("min((on+89)/89,1)", fc)  # previous scene frozen at its last Ken Burns frame
        self.assertIn("d=15:s=1920x1080", fc)  # 0.5 s transition
        self.assertIn("[prev][base]xfade=transition=smoothleft:duration=0.500:offset=0[xf]", fc)
        self.assertIn("fade=t=out:st=3.400:d=1.0", fc)
        flash = render.scene_clip_cmd("ffmpeg", self.spec(transition="fadewhite", prev_image=Path("p.png"),
                                                          prev_motion="zoom_in", prev_frames=60, fade_in=True))
        ffc = flash[flash.index("-filter_complex") + 1]
        self.assertIn("xfade=transition=fadewhite:duration=0.200", ffc)
        self.assertIn("fade=t=in:st=0:d=0.15", ffc)  # starts almost instantly

    def test_transition_planning(self):
        class S:
            def __init__(self, beat="normal", tr=""):
                self.beat_type, self.transition_in = beat, tr

        self.assertEqual(render.plan_transition(0, S()), "")
        self.assertEqual(render.plan_transition(1, S("hook")), "")
        self.assertEqual(render.plan_transition(5, S("punchline")), "fadewhite")
        self.assertEqual(render.plan_transition(5, S(tr="cut")), "")
        self.assertEqual(render.plan_transition(5, S(tr="circleopen")), "circleopen")
        used = set()
        self.assertEqual(render.plan_transition(3, S(tr="pixelize"), used), "pixelize")
        self.assertEqual(render.plan_transition(4, S(tr="pixelize"), used), "fade")  # jarring: once per video
        autos = {render.plan_transition(i, S()) for i in range(1, 17)}
        self.assertIn("", autos)  # some hard cuts for rhythm
        self.assertIn("fade", autos)
        self.assertEqual(render.transition_sfx_tag("smoothleft"), "whoosh")
        self.assertIsNone(render.transition_sfx_tag("smoothleft", "whoosh"))
        self.assertIsNone(render.transition_sfx_tag("fade"))
        self.assertEqual(render.transition_sfx_tag("fadewhite"), "impact")
        self.assertIsNone(render.transition_sfx_tag("fadeblack"))
        # new Scene.Transition names map to xfade names
        self.assertEqual(render.plan_transition(5, S(tr="crossfade")), "fade")
        self.assertEqual(render.plan_transition(5, S(tr="whip")), "smoothleft")
        self.assertEqual(render.plan_transition(5, S(tr="dip_to_black")), "fadeblack")
        self.assertEqual(render.plan_transition(5, S(tr="flash")), "fadewhite")
        self.assertEqual(render.transition_duration("smoothleft", whip=True), render.WHIP_SEC)

    def test_scene_sfx_items(self):
        class S:
            sfx = [{"tag": "ding", "offset_ms": 900, "gain_db": -12}, {"tag": "kaboom"}, "junk",
                   {"tag": "whoosh", "offset_ms": -5, "gain_db": 99}]

        items = render.scene_sfx_items(S())
        self.assertEqual(items, [{"tag": "whoosh", "offset_ms": 0, "gain_db": 6.0},
                                 {"tag": "ding", "offset_ms": 900, "gain_db": -12.0}])
        self.assertAlmostEqual(render.db_to_gain(-6), 0.501, places=3)

    def test_concat_and_music(self):
        txt = render.concat_list([Path("/x/it's.mp4")])
        self.assertIn("file '", txt)
        self.assertIn("it'\\''s.mp4", txt)
        m = render.music_mix_cmd("ffmpeg", Path("v.mov"), Path("o.mp4"), 60.0, Path("m.mp3"))
        self.assertIn("-stream_loop", m)
        fc = m[m.index("-filter_complex") + 1]
        self.assertIn("volume=-15.0dB", fc)
        self.assertIn("afade=t=out:st=57.00:d=3", fc)
        self.assertIn("sidechaincompress", fc)  # music ducks under the voice
        self.assertIn("loudnorm=I=-14.0", fc)
        self.assertEqual(m[m.index("-c:v") + 1], "copy")
        plain = render.music_mix_cmd("ffmpeg", Path("v.mov"), Path("o.mp4"), 60.0, None)
        self.assertNotIn("-stream_loop", plain)
        self.assertIn("loudnorm", plain[plain.index("-filter_complex") + 1])
        self.assertEqual(plain[plain.index("-c:a") + 1], "aac")

    def test_codec_choice(self):
        self.assertEqual(render.video_codec_args("final", {"qsv": True})[:2], ["-c:v", "h264_qsv"])
        self.assertIn("libx264", render.video_codec_args("preview", {"qsv": False}))


class SubtitleTests(TestCase):
    def test_grouping(self):
        words = "It's 3 a.m. You're running, but your legs feel like wet sand.".split()
        groups = subtitles.group_words(words)
        self.assertTrue(all(3 <= len(g) <= 8 for g in groups))
        self.assertEqual(sum(len(g) for g in groups), len(words))

    def test_proportional_timing_covers_duration(self):
        t = subtitles.proportional_timings("one two three four", 4.0)
        self.assertEqual(t[0]["start"], 0)
        self.assertAlmostEqual(t[-1]["end"], 4.0, places=2)

    def test_events_from_word_timings_and_hook_style(self):
        wt = [{"word": w, "start": i * 0.5, "end": i * 0.5 + 0.4} for i, w in enumerate("a b c d e f g h".split())]
        ev = subtitles.caption_events("a b c d e f g h", 4.2, wt)
        self.assertEqual(ev[0][0], 0.0)
        self.assertEqual(ev[-1][1], 4.2)
        self.assertIn("Style: Hook", subtitles.scene_ass("x y z", 2, None, hook=True))
        self.assertIn(",Hook,", subtitles.scene_ass("x y z", 2, None, hook=True))
        self.assertIn(",Default,", subtitles.scene_ass("x y z", 2, None))

    def test_karaoke_highlights_spoken_word(self):
        wt = [{"word": w, "start": i * 0.5, "end": i * 0.5 + 0.4} for i, w in enumerate("one two three four".split())]
        ass = subtitles.scene_ass("one two three four", 2.5, wt)
        events = [l for l in ass.splitlines() if l.startswith("Dialogue:")]
        self.assertEqual(len(events), 4)  # one event per spoken word
        self.assertIn(r"{\1c&H0000E5FF&}two{\1c&H00FFFFFF&}", events[1])
        self.assertTrue(events[0].endswith("three four"))
        self.assertIn(r"\fad(60,0)", events[0])  # pop-in only when the caption appears
        self.assertNotIn(r"\fad", events[1])
        self.assertTrue(events[-1].startswith("Dialogue: 0,0:00:01.50,0:00:02.50"))
        self.assertEqual(subtitles.ass_time(3725.5), "1:02:05.50")

    def test_elevenlabs_alignment(self):
        chars = list("Hi you")
        w = words_from_alignment(chars, [0, .1, .2, .3, .4, .5], [.1, .2, .3, .4, .5, .6])
        self.assertEqual([(x.word, x.start, x.end) for x in w], [("Hi", 0, 0.2), ("you", 0.3, 0.6)])

    def test_elevenlabs_alignment_skips_audio_tags(self):
        chars = list("[whispers] Hi you")
        n = len(chars)
        w = words_from_alignment(chars, [i / 10 for i in range(n)], [(i + 1) / 10 for i in range(n)])
        self.assertEqual([x.word for x in w], ["Hi", "you"])
        self.assertEqual(w[0].start, 1.1)

    def test_elevenlabs_request_body_acts_the_line(self):
        from apps.videos.services.tts.elevenlabs import ElevenLabsProvider, take_is_sane
        from apps.videos.services.voice_style import VoiceStyle

        v3 = ElevenLabsProvider("k", "v", "eleven_v3").request_body("They were not alone.", VoiceStyle("whisper", 2, "slow"))
        self.assertEqual(v3["text"], "[whispers][slowly] They were not alone.")
        plain = ElevenLabsProvider("k", "v", "eleven_v3").request_body("Hello there, friend.", None)
        self.assertEqual(plain["text"], "Hello there, friend.")
        v2 = ElevenLabsProvider("k", "v", "eleven_multilingual_v2").request_body("Wow, look!", VoiceStyle("excited", 2, "fast"))
        self.assertNotIn("[", v2["text"])
        self.assertGreater(v2["voice_settings"]["speed"], 1.0)
        self.assertTrue(take_is_sane("One two three four five six", 2.0))
        self.assertFalse(take_is_sane("One two three four five six", 0.5))  # cut off
        self.assertFalse(take_is_sane("One two three four five six", 9.0))  # stretched / garbled


class EdgeProviderTests(TestCase):
    def test_word_boundaries_and_file(self):
        from apps.videos.services.tts.edge import EdgeTTSProvider

        class FakeComm:
            def __init__(self, text, voice, boundary, connector=None, rate="+0%", pitch="+0Hz", volume="+0%"):
                assert boundary == "WordBoundary"
                assert connector is not None  # OS resolver connector (Windows DNS fix)

            async def stream(self):
                yield {"type": "audio", "data": b"ID3fake"}
                yield {"type": "WordBoundary", "offset": 1_000_000, "duration": 4_000_000, "text": "Hello"}
                yield {"type": "WordBoundary", "offset": 6_000_000, "duration": 3_000_000, "text": "world"}

        with tempfile.TemporaryDirectory() as tmp, mock.patch("edge_tts.Communicate", FakeComm), \
                mock.patch.object(media_library, "audio_duration", return_value=1.2):
            res = EdgeTTSProvider("en-US-GuyNeural").synthesize("Hello world", Path(tmp) / "x.wav")
            self.assertEqual(res.path.suffix, ".mp3")
            self.assertEqual(res.path.read_bytes(), b"ID3fake")
        self.assertEqual([(w.word, w.start, w.end) for w in res.word_timings], [("Hello", 0.1, 0.5), ("world", 0.6, 0.9)])
        self.assertEqual(res.duration, 1.2)


class FakeTTS:
    """Makes a real tone with ffmpeg so the render path is exercised end to end."""
    name = "fake"
    extension = ".wav"

    def synthesize(self, text, out_path):
        out = Path(out_path).with_suffix(".wav")
        dur = max(1.0, len(text.split()) * 0.25)
        subprocess.run([render.ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                        f"sine=frequency=440:duration={dur}", "-ar", "24000", str(out)], check=True)
        words = text.split()
        return TTSResult(out, dur, [WordTiming(w, i * 0.25, i * 0.25 + 0.2) for i, w in enumerate(words)])


@override_settings(MEDIA_ROOT=TMP_MEDIA, CLOUDFLARE_ACCOUNT_ID="", CLOUDFLARE_API_TOKEN="")
class EndToEndRenderTests(TestCase):
    def test_produce_video_real_ffmpeg(self):
        media_library.import_starter_pack()
        p = Project.objects.create(topic="Render test", niche=Niche.active(), status=Project.Status.APPROVED,
                                   script_json={"mood": "mysterious"})
        texts = ["It's 3 a.m. and something is behind you.", "Your brain rehearses danger at night.",
                 "Sleep well, your ancestors outran it first."]
        for i, t in enumerate(texts, start=1):
            p.scenes.create(order=i, narration=t, beat_type="hook" if i == 1 else "normal",
                            sfx=[{"tag": "whoosh", "offset_ms": 300, "gain_db": -8}] if i == 2 else [],
                            transition_in="whip" if i == 3 else "")
        with mock.patch("apps.videos.services.tts.get_tts", return_value=FakeTTS()):
            tasks.produce_video(p.pk, "preview")
        p.refresh_from_db()
        self.assertEqual(p.status, Project.Status.APPROVED, p.error_message)
        self.assertTrue(p.preview_video)
        self.assertIsNotNone(p.music_track)
        out = Path(p.preview_video.path)
        probe = subprocess.run([render.ffmpeg_exe(), "-hide_banner", "-i", str(out)], capture_output=True, text=True).stderr
        self.assertIn("Video: h264", probe)
        self.assertIn("1280x720", probe)
        self.assertIn("Audio: aac", probe)
        dur = media_library.audio_duration(out)
        self.assertAlmostEqual(dur, p.actual_duration_sec, delta=0.5)
        # second run re-uses cached clips (fast) and the final 1080p render marks the project done
        with mock.patch("apps.videos.services.tts.get_tts", return_value=FakeTTS()):
            tasks.produce_video(p.pk, "final")
        p.refresh_from_db()
        self.assertEqual(p.status, Project.Status.DONE, p.error_message)
        self.assertIn("1920x1080", subprocess.run([render.ffmpeg_exe(), "-hide_banner", "-i", p.final_video.path],
                                                  capture_output=True, text=True).stderr)
        self.assertFalse(p.has_unrendered_changes)
        self.assertTrue(all(s.clip_hash for s in p.scenes.all()))

    def test_hook_scene_uses_video_clip(self):
        media_library.import_starter_pack()
        p = Project.objects.create(topic="Hook video test", niche=Niche.active(), status=Project.Status.APPROVED,
                                   script_json={"mood": "mysterious"})
        clip = Path(TMP_MEDIA) / "hook_src.mp4"
        clip.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([render.ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                        "testsrc=size=640x360:rate=24:duration=1", "-pix_fmt", "yuv420p", str(clip)], check=True)
        for i, t in enumerate(["Forty thousand years ago something watched.", "It never blinked.",
                               "Here is how we know that story."], start=1):
            p.scenes.create(order=i, narration=t, beat_type="hook" if i < 3 else "normal")
        from apps.videos.services import hook_video

        class Up:
            name = "002.mp4"

            def read(self):  # a 1 s clip, shorter than the line: the last frame is held
                return clip.read_bytes()

        hook_video.save_uploaded(p.scenes.get(order=2), Up())
        self.assertTrue(p.scenes.get(order=2).video)
        with mock.patch("apps.videos.services.tts.get_tts", return_value=FakeTTS()):
            tasks.produce_video(p.pk, "preview")
        p.refresh_from_db()
        self.assertEqual(p.status, Project.Status.APPROVED, p.error_message)
        self.assertTrue(p.preview_video)
        self.assertIn("Video: h264", subprocess.run([render.ffmpeg_exe(), "-hide_banner", "-i", p.preview_video.path],
                                                    capture_output=True, text=True).stderr)

    def test_elevenlabs_failure_falls_back_to_edge_for_the_whole_video(self):
        from apps.videos.services.tts import TTSError

        class Dead:
            name = "elevenlabs"
            extension = ".mp3"
            supports_style = True

            def synthesize(self, text, out_path, style=None):
                raise TTSError("ElevenLabs xatosi 401: invalid key")

        p = Project.objects.create(topic="Fallback", niche=Niche.active(), tts_provider="elevenlabs",
                                   status=Project.Status.APPROVED)
        for i, t in enumerate(["The first line is here.", "The second line follows it."], start=1):
            p.scenes.create(order=i, narration=t)
        with mock.patch("apps.videos.services.tts.get_tts",
                        side_effect=lambda name, project=None: Dead() if name == "elevenlabs" else FakeTTS()),                 mock.patch("apps.videos.tasks.time.sleep"):
            note, failed = tasks._generate_assets(p, lambda m: None, images=False)
        p.refresh_from_db()
        self.assertEqual(failed, [])
        self.assertEqual(p.tts_provider, "edge")
        self.assertIn("Edge", note)
        self.assertTrue(all(s.audio for s in p.scenes.all()))

    def test_missing_voice_service_fails_cleanly(self):
        from apps.videos.services.tts import TTSError

        class Broken:
            name = "broken"
            extension = ".mp3"

            def synthesize(self, text, out_path):
                raise TTSError("Edge TTS ishlamadi")

        p = Project.objects.create(topic="Broken", status=Project.Status.APPROVED)
        p.scenes.create(order=1, narration="Hello there friend")
        with mock.patch("apps.videos.services.tts.get_tts", return_value=Broken()), \
                mock.patch.object(tasks, "VOICE_PAUSE_SEC", 0):
            tasks.produce_video(p.pk)
        p.refresh_from_db()
        self.assertEqual(p.status, Project.Status.FAILED)
        self.assertIn("Ovoz yaratilmadi", p.error_message)
        self.assertFalse(p.is_working)


class VoiceRecoveryTests(TestCase):
    def test_waits_after_connection_drop_and_continues(self):
        from apps.videos.services.tts import TTSError

        class Flaky:
            name = "flaky"
            extension = ".wav"
            calls = 0

            def synthesize(self, text, out_path):
                Flaky.calls += 1
                if 2 <= Flaky.calls <= 3:  # scene 2 fails twice (connection drop), then works again
                    raise TTSError("ClientConnectorDNSError")
                return FakeTTS().synthesize(text, out_path)

        with tempfile.TemporaryDirectory() as tmp, override_settings(MEDIA_ROOT=tmp):
            p = Project.objects.create(topic="Flaky", status=Project.Status.APPROVED)
            for i in range(1, 4):
                p.scenes.create(order=i, narration=f"Scene number {i} here")
            msgs = []
            with mock.patch("apps.videos.services.tts.get_tts", return_value=Flaky()), \
                    mock.patch.object(tasks, "VOICE_PAUSE_SEC", 0):
                failed = tasks._generate_missing_voice(p, msgs.append)
            self.assertEqual(failed, [])
            self.assertTrue(all(s.audio for s in p.scenes.all()))
            self.assertTrue(any("kutib qayta" in m for m in msgs))

    def test_edge_waits_between_attempts(self):
        from apps.videos.services.tts import TTSError
        from apps.videos.services.tts.edge import EdgeTTSProvider

        prov = EdgeTTSProvider("v")
        with mock.patch("apps.videos.services.tts.edge.asyncio.run", side_effect=OSError("dns")), \
                mock.patch("apps.videos.services.tts.edge.time.sleep") as sl, tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(TTSError):
                prov.synthesize("hi", Path(tmp) / "a.mp3")
        self.assertEqual([c.args[0] for c in sl.call_args_list], [3, 8])


class SubscribeCtaTests(TestCase):
    def test_plan_mid_and_end(self):
        from apps.videos.services import cta

        durs = [5.0] * 20  # 100 s video
        beats = ["hook", "hook"] + ["normal"] * 7 + ["punchline"] + ["normal"] * 10
        plan = cta.plan(durs, beats)
        self.assertEqual(list(plan), [8])  # once: the first calm scene starting at >= 40 s
        beats[8] = "punchline"
        self.assertEqual(list(cta.plan(durs, beats)), [9 if beats[9] == "normal" else 10])
        self.assertEqual(cta.plan([3.0] * 5, ["normal"] * 5), {})  # short scenes, short video: no CTA
        short = cta.plan([5.0] * 7, ["hook"] * 7)  # no calm scene after 40 s: the last scene is the fallback
        self.assertEqual(list(short), [6])
        self.assertLessEqual(short[6] + cta.DURATION, 5.0 - render.FADE_OUT_SEC)
        with override_settings(SUBSCRIBE_CTA=False):
            self.assertEqual(cta.plan(durs, beats), {})
        with override_settings(SUBSCRIBE_CTA_END=False):
            self.assertEqual(cta.plan([5.0] * 7, ["hook"] * 7), {})

    def test_plan_lands_on_the_spoken_subscribe_line(self):
        from apps.videos.services import cta

        durs = [5.0] * 20
        beats = ["normal"] * 20
        texts = ["Plain fact."] * 20
        texts[4] = "Quick pause. If you enjoy this, tap subscribe, it is free and it takes one second."
        texts[19] = "Thanks for watching, subscribe and like, see you next time."
        plan = cta.plan(durs, beats, texts)
        self.assertIn(4, plan)  # the scene that says "subscribe", well before the 40 s timer
        self.assertNotIn(8, plan)
        self.assertGreater(plan[4], cta.LEAD)  # starts when the word is spoken, not at the scene start
        self.assertLessEqual(plan[4] + cta.DURATION, 5.0)
        self.assertEqual(list(plan), [4])  # only once, even though the last scene also says it
        self.assertIn(8, cta.plan(durs, beats, ["Plain fact."] * 20))  # no spoken line: falls back to the timer

    def test_like_follows_the_subscribe_and_returns_at_the_spoken_like(self):
        from apps.videos.services import cta

        durs = [5.0] * 5 + [16.0] + [5.0] * 10 + [14.0]
        texts = ["Plain."] * len(durs)
        texts[5] = "Quick pause. If you enjoy this, subscribe and stay with me. It's free and it takes one second."
        texts[-1] = "Thanks for staying. If it made you think, like the video and tell me in the comments. See you soon."
        sub = cta.plan(durs, ["normal"] * len(durs), texts)
        likes = cta.plan_likes(durs, texts, sub)
        self.assertEqual(list(sub)[0], 5)
        self.assertEqual(likes[5], round(sub[5] + cta.LIKE_AFTER_SUBSCRIBE, 3))  # same scene, right after the subscribe
        self.assertLessEqual(likes[5] + cta.LIKE_DURATION, durs[5])
        last = len(durs) - 1
        self.assertIn(last, likes)  # the closing "like the video"
        self.assertLessEqual(likes[last] + cta.LIKE_DURATION, durs[last] - render.FADE_OUT_SEC)
        lines = "".join(cta.like_events(likes[5]))
        self.assertIn("LIKED", lines)
        # a short subscribe scene hands the like to the next scene
        short = cta.plan_likes([5.0] * 12, ["Plain."] * 12, {3: 0.35})
        self.assertEqual(short, {4: cta.LEAD})
        with override_settings(SUBSCRIBE_CTA=False):
            self.assertEqual(cta.plan_likes(durs, texts, sub), {})

    def test_events_are_valid_ass(self):
        from apps.videos.services import cta

        lines = cta.events(0.35)
        self.assertTrue(all(l.startswith("Dialogue: ") for l in lines))
        text = "".join(lines)
        self.assertIn("SUBSCRIBE", text)
        self.assertIn("SUBSCRIBED", text)
        self.assertIn(r"\move(", text)
        self.assertEqual([s.tag for s in cta.SOUNDS], ["pop", "click", "click", "ding"])


class VoiceStyleTests(TestCase):
    def test_emotion_intensity_pace_to_edge(self):
        from apps.videos.services.voice_style import VoiceStyle

        self.assertEqual(VoiceStyle().edge_params(), {"rate": "+0%", "pitch": "+0Hz", "volume": "+0%"})
        tense = VoiceStyle("tense", 3, "slow").edge_params("+5%")
        self.assertTrue(tense["rate"].startswith("-") and tense["pitch"].startswith("-"))
        self.assertEqual(VoiceStyle("excited", 3, "fast").edge_params("+20%")["rate"], "+25%")  # clamped
        self.assertEqual(VoiceStyle("nonsense").edge_params()["rate"], "+0%")
        self.assertIn("suspenseful", VoiceStyle("tense").gemini_words())

    def test_style_reaches_edge_and_skips_plain_providers(self):
        from apps.videos.services import voice
        from apps.videos.services.tts.edge import EdgeTTSProvider
        from apps.videos.services.voice_style import VoiceStyle

        seen = {}

        class FakeComm:
            def __init__(self, text, voice, boundary, connector=None, **prosody):
                seen.update(prosody)

            async def stream(self):
                yield {"type": "audio", "data": b"ID3fake"}

        with tempfile.TemporaryDirectory() as tmp, mock.patch("edge_tts.Communicate", FakeComm), \
                mock.patch.object(media_library, "audio_duration", return_value=1.0):
            voice.synthesize(1, "Hello", EdgeTTSProvider("v", "+0%"), Path(tmp), VoiceStyle("sad", 2, "slow"))
            self.assertEqual(seen, {"rate": "-16%", "pitch": "-3Hz", "volume": "-6%"})
            plain = FakeTTS()  # no supports_style -> called without the style argument
            voice.synthesize(2, "Hello there", plain, Path(tmp), VoiceStyle("sad"))

    def test_delivery_change_drops_cached_voice(self):
        from django.core.files.base import ContentFile

        from apps.videos.services import director

        with tempfile.TemporaryDirectory() as tmp, override_settings(MEDIA_ROOT=tmp):
            p = Project.objects.create(topic="Voice cache")
            s = p.scenes.create(order=1, narration="Hello there friend")
            s.audio.save("a.mp3", ContentFile(b"x"))
            director.apply(p, [{"emotion": "tense", "intensity": 3, "pace": "slow"}])
            s.refresh_from_db()
            self.assertFalse(s.audio)
            self.assertEqual(s.emotion, "tense")


class MontageV4Tests(TestCase):
    def spec(self, **kw):
        base = dict(image=Path("img.png"), audio=Path("a.mp3"), out=Path("out.mp4"), duration=10.0, motion="zoom_in",
                    size=(1920, 1080), prescale=1.5, codec_args=["-c:v", "libx264"])
        base.update(kw)
        return render.ClipSpec(**base)

    def test_camera_moves_from_director(self):
        class S:
            def __init__(self, move=""):
                self.camera_move = move

        self.assertEqual(render.motion_for_scene(5, S("shake")), "shake")
        self.assertEqual(render.motion_for_scene(5, S("none")), "still")
        self.assertEqual(render.motion_for_scene(0, S()), "punch")  # the video opens with a punch-in
        auto = render.motion_for_scene(3, S())
        self.assertNotEqual(render.motion_for_scene(3, S(), prev_motion=auto), auto)
        z, x, y = render.zoompan_expr("shake", 100)
        self.assertIn("sin(", x)
        self.assertIn("max(0,1-(on+0)/10)", x)
        # frozen final frame for transitions: the shake has died out, the punch has landed
        self.assertIn("min((on+99)/8,1)", render.zoompan_expr("punch", 100, offset=99)[0])

    def test_scene_cut_into_framings(self):
        words = [{"word": "w", "start": round(i * 0.4, 3), "end": round(i * 0.4 + 0.3, 3)} for i in range(25)]
        starts = [w["start"] for w in words]
        self.assertEqual(render.split_points(2.6, 2.4, words, hook=True), [])  # a 2-3 s hook line is already one new picture
        hook = render.split_points(4.6, 4.4, words, hook=True)      # longer hook line: a new view every ~2 s
        self.assertEqual(len(hook), 1)
        self.assertIn(hook[0], [w["start"] for w in words])           # cut lands on a word start
        self.assertEqual(len(render.split_points(6.6, 6.4, words, hook=True)), 2)
        body = render.split_points(8.4, 8.0, words, hook=False)     # later: a new view every ~3.5 s
        self.assertEqual(len(body), 1)
        self.assertTrue(3.0 <= body[0] <= 5.5)
        self.assertEqual(render.split_points(3.0, 2.8, words, hook=False), [])
        self.assertEqual(render.split_points(1.4, 1.2, words, hook=True), [])
        shots = render.shot_list("punch", 5.0, [1.6, 3.2])
        self.assertEqual([m for m, _ in shots], ["punch", "jump", "jump_l"])  # rotating framings
        self.assertEqual(sum(f for _, f in shots), render.frame_count(5.0))

    def test_two_shot_command(self):
        cmd = render.scene_clip_cmd("ffmpeg", self.spec(shots=[("punch", 120), ("jump", 180)], vignette=True,
                                                        subtitles="s.ass", fonts_dir="fonts"))
        fc = cmd[cmd.index("-filter_complex") + 1]
        self.assertIn("split=2[s0][s1]", fc)
        self.assertIn("d=120:", fc)
        self.assertIn("d=180:", fc)
        self.assertIn("[k0][k1]concat=n=2:v=1:a=0,settb=1/30[base]", fc)
        self.assertIn("vignette=angle=PI/7,ass=s.ass:fontsdir=fonts[v]", fc)

    def test_music_cues_and_delayed_start(self):
        expr = render.music_gain_expr([(10.0, 18.0, 0.12, 0.4), (30.0, 40.0, 1.7, 1.0)])
        self.assertIn("clip((t-10.00)/0.4,0,1)", expr)
        self.assertIn("(1+(1.7-1)*", expr)
        m = render.music_mix_cmd("ffmpeg", Path("v.mov"), Path("o.mp4"), 60.0, Path("m.mp3"), music_start=6.5,
                                 gain_expr=expr)
        fc = m[m.index("-filter_complex") + 1]
        self.assertIn("adelay=6500|6500,afade=t=in:st=6.50:d=0.6", fc)
        self.assertIn(f"volume='{expr}':eval=frame", fc)
        self.assertIsNone(render.music_gain_expr([]))

    def test_on_screen_text_and_stats(self):
        from apps.videos.services import overlays

        plain = "".join(overlays.events("night made us", 6.0))
        self.assertIn("NIGHT MADE US", plain)
        self.assertIn(r"\fnBebas Neue", plain)
        counting = overlays.events("200,000 years", 6.0)
        texts = [l for l in counting if "YEARS" in l]
        self.assertEqual(len(texts), overlays.COUNT_STEPS)
        self.assertIn("200,000", texts[-1])
        self.assertNotIn("200,000", texts[0])  # starts low and counts up
        self.assertEqual(overlays.percent_of("80 PERCENT"), 80.0)
        bar = "".join(overlays.events("80%", 6.0))
        self.assertIn(r"\clip(", bar)
        self.assertEqual(overlays.events("x", 0.8), [])  # scene too short

    def test_srt(self):
        srt = subtitles.srt_for_scenes([(0.0, "one two three four", 2.0, None), (62.5, "five six seven", 1.5, None)])
        self.assertTrue(srt.startswith("1\n00:00:00,000 --> "))
        self.assertIn("00:01:02,500 -->", srt)


class RealFfmpegShotsTests(TestCase):
    def test_two_shots_after_a_transition_render(self):
        """Regression: a split scene entered with an xfade failed (concat timebase != zoompan timebase)."""
        from PIL import Image

        exe = render.ffmpeg_exe()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            for name, colour in (("a.png", "red"), ("b.png", "blue")):
                Image.new("RGB", (320, 180), colour).save(tmp / name)
            subprocess.run([exe, "-y", "-loglevel", "error", "-f", "lavfi", "-i", "sine=frequency=300:duration=3",
                            str(tmp / "v.wav")], check=True)
            spec = render.ClipSpec(image=tmp / "b.png", audio=tmp / "v.wav", out=tmp / "o.mov", duration=3.0,
                                   motion="punch", size=(320, 180), prescale=1.5,
                                   codec_args=["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p"],
                                   shots=[("punch", 40), ("jump", 50)], vignette=True, transition="fade",
                                   prev_image=tmp / "a.png", prev_motion="jump", prev_frames=60)
            render._run(render.scene_clip_cmd(exe, spec), cwd=tmp)
            self.assertAlmostEqual(media_library.audio_duration(tmp / "o.mov"), 3.0, delta=0.15)


class CaptionToggleTests(TestCase):

    def test_no_captions_leaves_only_the_header(self):
        words = [{"word": "Hello", "start": 0.0, "end": 0.4}]
        with_caps = subtitles.scene_ass("Hello", 1.0, words)
        self.assertIn("Dialogue", with_caps)
        self.assertNotIn("Dialogue", subtitles.ASS_HEADER)


class AtmosphereTests(TestCase):
    def test_effect_from_prompt_and_indoor_rule(self):
        from types import SimpleNamespace as NS

        from apps.videos.services import atmosphere as a

        self.assertEqual(a.effect_for(NS(image_prompt="Heavy rain over a forest", narration="")), "rain")
        self.assertEqual(a.effect_for(NS(image_prompt="Lightning over hills in the rain", narration="")), "storm")
        self.assertEqual(a.effect_for(NS(image_prompt="A small fire under a rock overhang while rain falls outside", narration="")), "fire")
        self.assertEqual(a.effect_for(NS(image_prompt="He lies in bed while rain streaks down a window", narration="")), "")
        self.assertEqual(a.effect_for(NS(image_prompt="A grassy meadow", narration="Snow fell all night.")), "snow")
        self.assertEqual(a.effect_for(NS(image_prompt="A grassy meadow", narration="Nice day.")), "")

    def test_clip_command_overlays_loop_and_flickers(self):
        from unittest import mock

        from apps.videos.services import atmosphere as a

        spec = render.ClipSpec(image=Path("i.png"), audio=Path("a.wav"), out=Path("o.mov"), duration=3.0, motion="in",
                               size=(1920, 1080), prescale=1.5, codec_args=[], atmosphere="storm", seed=4)
        with mock.patch.object(a, "overlay_path", return_value=Path("rain.mov")):
            cmd = render.scene_clip_cmd("ffmpeg", spec)
        fc = cmd[cmd.index("-filter_complex") + 1]
        self.assertIn("-stream_loop", cmd)
        self.assertIn("overlay=0:0:shortest=1", fc)
        self.assertIn("eq=brightness='if(lt(mod(", fc)
        spec.atmosphere = "fire"
        cmd = render.scene_clip_cmd("ffmpeg", spec)
        self.assertNotIn("-stream_loop", cmd)
        self.assertIn("sin(2*PI*t", cmd[cmd.index("-filter_complex") + 1])
