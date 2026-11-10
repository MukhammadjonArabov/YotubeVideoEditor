import json
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.videos.management.commands.video_import import check_script
from apps.videos.models import Niche, Project
from apps.videos.services import align, originality
from apps.videos.services import script as sc


def scene(i, kind=None, text=None, source="Smith (2020)"):
    kind = kind or ("hero" if i % 2 == 0 else "fact")
    return {
        "narration": text or f"Scene {i} tells a brand new thing number {i} about the long ancient night and its odd ways.",
        "image_prompt": f"The main character doing thing {i}" if kind == "hero" else f"A fossil on a rock, view {i}",
        "beat_type": "normal", "sfx_cue": None, "scene_kind": kind,
        "fact_source": source if kind == "fact" else None,
    }


HOOK_LINES = ["Twelve hours of darkness, every single night.", "Something out there could see you perfectly.",
              "Your phone keeps you up until one.", "That problem started long before phones.",
              "Your sleep troubles have an ancient cause.", "Tonight you'll learn where it comes from.",
              "You'll see how fire changed every night.", "And why stories belong to the dark.",
              "You'll even sleep a little better after this.", "But first, one strange camp in Tanzania.",
              "Everyone there slept at once for eighteen minutes.", "Why only eighteen? Stay with me."]


def script_json(n=11, hook=True, **kw):
    """A valid 2-minute script by default: 12 one-sentence hook scenes + `n` normal scenes."""
    scenes = [scene(i) for i in range(n)]
    if hook:
        hook_scenes = [scene(i, text=line) for i, line in enumerate(HOOK_LINES)]
        for s in hook_scenes:
            s["beat_type"] = "hook"
        scenes = hook_scenes + [scene(len(HOOK_LINES) + i) for i in range(n)]
    data = {"title": "What Did Ancient Humans Do After DARK?", "title_alternatives": ["A", "B", "C", "D", "E"],
            "description": "D.\n\nSources:", "tags": ["a", "b"], "mood": "mysterious", "sources": ["X (2020)"],
            "scenes": scenes}
    data.update(kw)
    return data


class AlignMappingTests(TestCase):
    def test_script_words_keep_spelling_and_get_whisper_times(self):
        heard = [("Picture", 0.0, 0.4), ("this.", 0.4, 0.8), ("The", 1.0, 1.1), ("Joe", 1.1, 1.5),
                 ("hoansi", 1.5, 1.9), ("talk.", 2.0, 2.4)]
        out = align.map_to_script("Picture this. The Ju'hoansi people talk.", heard, 3.0)
        self.assertEqual([w["word"] for w in out], ["Picture", "this.", "The", "Ju'hoansi", "people", "talk."])
        self.assertEqual((out[0]["start"], out[1]["end"]), (0.0, 0.8))
        self.assertEqual(out[5]["start"], 2.0)  # matched again after the misheard name
        self.assertTrue(1.1 <= out[3]["start"] < out[4]["start"] < 2.0)  # gap filled in order
        self.assertTrue(all(w["end"] > w["start"] for w in out))

    def test_nothing_heard_spreads_over_duration(self):
        out = align.map_to_script("one two three", [], 3.0)
        self.assertEqual(out[0]["start"], 0.0)
        self.assertAlmostEqual(out[-1]["end"], 3.0, places=2)


class OriginalityTests(TestCase):
    def test_overlap_share(self):
        p = Project.objects.create(topic="Old video")
        p.scenes.create(order=1, narration="our ancestors slept in trees to stay away from hungry leopards at night")
        res = originality.script_overlap(["Our ancestors slept in trees to stay away from hungry leopards. New words here."])
        self.assertEqual(res[0].project_id, p.pk)
        self.assertGreater(res[0].share, 0.5)
        self.assertEqual(originality.script_overlap(["Totally different sentence about cooking fish over hot stones."]), [])


@override_settings(MAX_SCRIPT_OVERLAP=0.08, MAX_IMAGES_PER_PROJECT=160)
class CheckScriptTests(TestCase):
    def test_good_script_passes(self):
        data = sc.ScriptOut.model_validate(script_json())
        problems, warnings = check_script(data, minutes=2, seconds_per_image=8)
        self.assertEqual(problems, [])

    def test_blocking_problems(self):
        bad = script_json()
        bad["scenes"][0]["narration"] = "Hello guys and welcome back to the channel, today we look at night."
        bad["scenes"] = [scene(i, kind="hero") for i in range(5)] + bad["scenes"][5:]
        bad["scenes"][0]["narration"] = "Hello guys and welcome back to the channel, today we look at night."
        data = sc.ScriptOut.model_validate(bad)
        problems, _ = check_script(data, minutes=5, seconds_per_image=8)
        text = " | ".join(problems)
        self.assertIn("sahnalar soni", text)     # 15 scenes for 5 min
        self.assertIn("salomlashish", text)
        self.assertIn("almashinuvi", text)

    def test_reused_phrases_block(self):
        old = Project.objects.create(topic="Older video")
        for i in range(15):
            old.scenes.create(order=i + 1, narration=script_json()["scenes"][i]["narration"])
        problems, _ = check_script(sc.ScriptOut.model_validate(script_json()), minutes=2, seconds_per_image=8)
        self.assertTrue(any("umumiy ibora" in p for p in problems))

    def test_missing_fact_source_warns(self):
        data = script_json()
        data["scenes"][1]["fact_source"] = None
        _, warnings = check_script(sc.ScriptOut.model_validate(data), minutes=2, seconds_per_image=8)
        self.assertTrue(any("manbasi yo'q" in w and "2" in w for w in warnings))


@override_settings(MAX_SCRIPT_OVERLAP=0.08, MAX_IMAGES_PER_PROJECT=160, TTS_PROVIDER="edge")
class VideoImportCommandTests(TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "s.json"
        self.path.write_text(json.dumps(script_json()), encoding="utf-8")
        (Path(self.tmp.name) / "idea.txt").write_text("Tunda nima qilishgan?", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def run_cmd(self, *extra):
        out = StringIO()
        call_command("video_import", str(self.path), "--minutes", "2", "--no-director", "--no-compliance",
                     *extra, stdout=out)
        return out.getvalue()

    def test_dry_run_saves_nothing(self):
        self.assertIn("--dry-run", self.run_cmd("--dry-run"))
        self.assertFalse(Project.objects.exists())

    def test_import_creates_project_with_idea_and_sources(self):
        out = self.run_cmd("--idea", str(Path(self.tmp.name) / "idea.txt"), "--concept", "Konsepsiya matni")
        p = Project.objects.get()
        self.assertIn(f"/videolar/{p.pk}/", out)
        self.assertEqual((p.status, p.script_author, p.target_duration_sec), ("script_ready", "claude", 120))
        self.assertEqual(p.idea, "Tunda nima qilishgan?")
        self.assertEqual(p.concept, "Konsepsiya matni")
        self.assertEqual(p.scenes.count(), 23)  # 12 one-sentence hook scenes + 11 normal ones
        self.assertEqual(p.scenes.get(order=2).fact_source, "Smith (2020)")
        self.assertEqual(list(p.scenes.filter(beat_type="hook").values_list("order", flat=True)), list(range(1, 13)))
        # re-import into the same project replaces the script instead of failing as a duplicate
        self.run_cmd("--project", str(p.pk))
        self.assertEqual(Project.objects.count(), 1)

    def test_bad_script_is_refused(self):
        self.path.write_text(json.dumps(script_json(4)), encoding="utf-8")
        with self.assertRaises(CommandError):
            self.run_cmd()
        self.assertFalse(Project.objects.exists())


class VideoCheckCommandTests(TestCase):
    def test_flags_repeated_topic(self):
        Project.objects.create(topic="How Did Ancient Humans Keep Their TEETH Clean?", niche=Niche.active())
        out = StringIO()
        call_command("video_check", "How did ancient humans keep teeth clean", "What did ancient humans do at night",
                     stdout=out)
        text = out.getvalue()
        self.assertIn("[TAKRORLANADI] How did ancient humans keep teeth clean", text)
        self.assertIn("[yangi] What did ancient humans do at night", text)
        self.assertIn("OLDINGI VIDEOLAR", text)
