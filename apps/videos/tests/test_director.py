from types import SimpleNamespace
from unittest import mock

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.videos.models import Project
from apps.videos.services import director, gemini_client


def scenes(n, words=12, beats=None):
    beats = beats or ["normal"] * n
    return [SimpleNamespace(narration=" ".join(["word"] * words), beat_type=beats[i]) for i in range(n)]


def d(emotion="neutral", sfx=(), **kw):
    base = {"emotion": emotion, "intensity": 2, "pace": "normal", "pause_after_ms": 0, "camera_move": "slow_zoom_in",
            "transition_in": "cut", "sfx": [{"tag": t, "offset_ms": 0, "gain_db": -8} for t in sfx],
            "music_cue": "continue", "on_screen_text": None}
    base.update(kw)
    return base


class EnforceRulesTests(TestCase):
    def test_bad_values_are_cleaned(self):
        out = director.enforce_rules([d("angry", intensity=9, pace="warp", pause_after_ms=99999, camera_move="spin",
                                        transition_in="star", music_cue="loud", on_screen_text="one two three four five",
                                        sfx=["kaboom", "ding", "ding"])], scenes(1))[0]
        self.assertEqual(out["emotion"], "neutral")
        self.assertEqual(out["intensity"], 3)
        self.assertEqual(out["pace"], "normal")
        self.assertEqual(out["pause_after_ms"], 1500)
        self.assertEqual(out["camera_move"], "")
        self.assertEqual(out["transition_in"], "cut")
        self.assertEqual(out["music_cue"], "continue")
        self.assertEqual(out["on_screen_text"], "ONE TWO THREE FOUR")
        self.assertEqual([x["tag"] for x in out["sfx"]], ["ding"])

    def test_no_more_than_three_same_emotions_in_a_row(self):
        out = director.enforce_rules([d("scared") for _ in range(8)], scenes(8))
        emotions = [x["emotion"] for x in out]
        run = best = 1
        for a, b in zip(emotions, emotions[1:]):
            run = run + 1 if a == b else 1
            best = max(best, run)
        self.assertLessEqual(best, director.MAX_SAME_EMOTION)
        self.assertEqual(emotions[3], "tense")  # scared -> its neighbour, not a random mood

    def test_same_sfx_never_twice_in_a_row(self):
        out = director.enforce_rules([d(sfx=["whoosh"]), d(sfx=["whoosh"]), d(sfx=["whoosh"])],
                                     scenes(3, beats=["punchline"] * 3))
        tags = [[x["tag"] for x in s["sfx"]] for s in out]
        for a, b in zip(tags, tags[1:]):
            self.assertFalse(set(a) & set(b))

    def test_sfx_density_keeps_punchlines(self):
        beats = ["normal", "punchline"] * 10
        out = director.enforce_rules([d(sfx=["pop" if i % 2 else "ding"]) for i in range(20)],
                                     scenes(20, beats=beats))
        with_sfx = [i for i, s in enumerate(out) if s["sfx"]]
        self.assertLessEqual(len(with_sfx), round(20 / director.SFX_EVERY))
        self.assertTrue(all(beats[i] == "punchline" for i in with_sfx))

    def test_music_cues_are_rationed(self):
        beats = ["normal", "punchline"] * 10
        dirs = [d(music_cue="stinger") for _ in range(20)]
        dirs[3]["music_cue"] = dirs[7]["music_cue"] = dirs[9]["music_cue"] = "change_mood"
        out = director.enforce_rules(dirs, scenes(20, beats=beats))
        cues = [(i, x["music_cue"]) for i, x in enumerate(out) if x["music_cue"] != "continue"]
        self.assertLessEqual(len(cues), round(20 / director.MUSIC_CUE_EVERY))
        self.assertLessEqual(sum(1 for _, c in cues if c == "change_mood"), director.MAX_MOOD_CHANGES)
        self.assertTrue(all(beats[i] == "punchline" for i, c in cues if c == "stinger"))

    def test_on_screen_text_is_rare(self):
        out = director.enforce_rules([d(on_screen_text="BIG") for _ in range(12)], scenes(12))
        self.assertEqual(sum(1 for x in out if x["on_screen_text"]), 2)

    def test_camera_no_repeats_and_few_stills(self):
        out = director.enforce_rules([d(camera_move="none") for _ in range(12)], scenes(12))
        moves = [x["camera_move"] for x in out]
        self.assertLessEqual(moves.count("none"), 2)
        out = director.enforce_rules([d(camera_move="pan_left") for _ in range(4)], scenes(4))
        self.assertEqual([x["camera_move"] for x in out], ["pan_left", "", "pan_left", ""])

    def test_pattern_interrupt_added_in_long_quiet_stretch(self):
        # 20 scenes x ~5.2 s with nothing happening -> a whip at least every PATTERN_GAP_SEC
        out = director.enforce_rules([d() for _ in range(20)], scenes(20, words=12))
        whips = [i for i, s in enumerate(out) if s["transition_in"] == "whip"]
        self.assertTrue(whips)
        per_scene = director.estimate_seconds(" ".join(["w"] * 12))
        gaps = [b - a for a, b in zip([0] + whips, whips + [20])]
        self.assertTrue(all(g * per_scene <= director.PATTERN_GAP_SEC + per_scene for g in gaps))
        self.assertEqual(out[0]["transition_in"], "cut")


@override_settings(GEMINI_API_KEY="k", GEMINI_TEXT_MODEL="m")
class DirectorJobTests(TestCase):
    def setUp(self):
        self.p = Project.objects.create(topic="Why did cavemen fear the dark?", script_json={"mood": "mysterious"})
        for i in range(1, 46):  # more than one batch
            self.p.scenes.create(order=i, narration=f"Scene {i} says something rather interesting here.")

    def fake(self, prompt, schema, **kw):
        import re

        idx = [int(x) for x in re.findall(r"^(\d+)\. \[", prompt, re.M)]
        return director.DirectionOut(scenes=[director.SceneDirection(
            index=i, emotion="awe" if i % 2 else "funny", intensity=2, pace="normal", camera_move="pan_left",
            transition_in="cut", sfx=[], music_cue="continue") for i in idx])



class AuthoredVoiceTests(TestCase):
    def test_script_author_voice_is_kept_by_the_director(self):
        from apps.videos.services import script as sc

        data = sc.ScriptOut(title="T", title_alternatives=[], description="", tags=[], mood="calm", scenes=[
            sc.SceneOut(narration="They never saw it coming.", image_prompt="a cave", beat_type="hook",
                        emotion="scared", intensity=3, pace="slow", pause_after_ms=600),
            sc.SceneOut(narration="Then came the morning.", image_prompt="a sunrise", beat_type="build"),
        ])
        p = Project.objects.create(topic="Authored voice")
        sc.save_script(p, data)
        first, second = p.scenes.order_by("order")
        self.assertEqual((first.emotion, first.intensity, first.pace, first.pause_after_ms), ("scared", 3, "slow", 600))
        self.assertEqual(second.emotion, "neutral")
        director.apply(p, [{"emotion": "happy", "intensity": 1, "pace": "fast", "pause_after_ms": 0},
                           {"emotion": "awe", "intensity": 2, "pace": "slow"}])
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertEqual((first.emotion, first.pace, first.pause_after_ms), ("scared", "slow", 600))  # author wins
        self.assertEqual((second.emotion, second.pace), ("awe", "slow"))  # director fills the rest
