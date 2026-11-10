from unittest import mock

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.videos import tasks
from apps.videos.models import ComplianceCheck, Niche, Project
from apps.videos.services import compliance, gemini_client
from apps.videos.services import director
from apps.videos.services import script as sc


def fake_directions(n=8):
    return director.DirectionOut(scenes=[
        director.SceneDirection(index=i, emotion="curious", intensity=2, pace="normal", camera_move="slow_zoom_in",
                                transition_in="cut", sfx=[{"tag": "ding", "offset_ms": 200}] if i == 3 else [],
                                music_cue="continue", on_screen_text="9 min" if i == 5 else None)
        for i in range(1, n + 1)])


def make_script(n=8, hook_everywhere=False, bad_sfx=False, mood="eerie", alternate=True):
    scenes = []
    for i in range(n):
        fact = alternate and i % 2 == 1
        scenes.append(sc.SceneOut(
            narration=f"Sentence number {i} with a few words in it.",
            image_prompt=f"a fossil skull on a rock, thing {i}" if fact else f"the main character doing thing {i}",
            beat_type="hook" if hook_everywhere else ("punchline" if i == 5 else "build"),
            sfx_cue="kaboom" if bad_sfx else ("whoosh" if i == 2 else None),
            scene_kind="fact" if fact else "hero",
        ))
    return sc.ScriptOut(title="Why Do We Have Nightmares?", title_alternatives=["A", "B", "Why Do We Have Nightmares?", "C", "D", "E", "F"],
                        description="Desc.\n\nSources:", tags=["history", " sleep "], mood=mood,
                        sources=["Walker, M. (2017). Why We Sleep."], scenes=scenes)


class ScriptMathTests(TestCase):
    def test_scene_count_and_budget(self):
        self.assertEqual(sc.scene_count(540, 8), 68)   # 9 min / 8 s
        self.assertEqual(sc.scene_count(10, 8), 3)     # at least 3
        self.assertEqual(sc.word_budget(540), 1350)    # 9 * 150
        self.assertEqual(sc.words_per_scene(540, 8), 19)
        self.assertTrue(sc.count_ok(62, 68))
        self.assertFalse(sc.count_ok(40, 68))

    def test_clean_script_rules(self):
        data = sc.clean_script(make_script(hook_everywhere=True, bad_sfx=True), default_mood="mysterious")
        beats = [s.beat_type for s in data.scenes]
        self.assertEqual(beats[0], "hook")
        self.assertNotIn("hook", beats[2:])       # hooks only in the first 1-2 scenes
        self.assertTrue(all(s.sfx_cue is None for s in data.scenes))  # unknown tag removed
        self.assertEqual(data.mood, "mysterious")  # 'eerie' not in vocabulary -> niche default
        self.assertEqual(len(data.title_alternatives), 5)
        self.assertNotIn("Why Do We Have Nightmares?", data.title_alternatives)
        self.assertEqual(data.tags, ["history", "sleep"])

    def test_hook_covers_30_40_seconds(self):
        self.assertEqual(sc.hook_scene_target(), 12)  # one short sentence each, ~3 s
        self.assertEqual(sc.expected_scene_count(1200, 8), 12 + 146)  # 20 min: hook + 8 s scenes
        short = [sc.SceneOut(narration="Your ancestors slept with one eye open.", image_prompt="x", beat_type="hook")
                 for _ in range(20)]
        self.assertEqual(sc.hook_scene_count_for(short), 13)  # 13 x ~2.95 s fits in 40 s
        long = [sc.SceneOut(narration=" ".join(["word"] * 30), image_prompt="x", beat_type="hook") for _ in range(9)]
        self.assertEqual(sc.hook_scene_count_for(long), 3)  # at least 3
        data = sc.clean_script(make_script(hook_everywhere=True), "mysterious", hook_scenes=4)
        self.assertEqual([s.beat_type for s in data.scenes[:5]], ["hook"] * 4 + ["build"])
        self.assertNotIn("hook", [s.beat_type for s in data.scenes[4:]])

    def test_fact_scenes_never_draw_the_hero(self):
        data = make_script(alternate=False)
        data.scenes[1].scene_kind = "fact"  # model said fact but still wrote the hero into the prompt
        data.scenes[2].scene_kind = "weird"
        data = sc.clean_script(data, "mysterious")
        self.assertNotIn("main character", data.scenes[1].image_prompt)
        self.assertIn("an ancient person", data.scenes[1].image_prompt)
        self.assertEqual(data.scenes[2].scene_kind, "hero")  # unknown kind -> read from the prompt

    def test_alternation_check(self):
        self.assertTrue(sc.alternation_ok(make_script(20).scenes))
        self.assertFalse(sc.alternation_ok(make_script(20, alternate=False).scenes))
        self.assertEqual(sc.same_kind_pairs(make_script(20, alternate=False).scenes), 19)

    def test_prompt_contains_niche_and_budget(self):
        p = Project.objects.create(topic="Why Do We Still Have Ancient Nightmares?", target_duration_sec=540, niche=Niche.active())
        prompt = sc.build_prompt(p, 70, 1350)
        self.assertIn("exactly 70 scenes", prompt)
        self.assertIn("1350", prompt)
        self.assertIn("Niche:", prompt)
        self.assertIn("personal-take", prompt)
        self.assertIn("THE HOOK = scenes 1-12", prompt)  # 12 one-sentence scenes, fast pictures
        self.assertIn("ONE sentence each", prompt)
        self.assertIn("Why watch", prompt)
        self.assertIn("What they get", prompt)
        self.assertIn("Open loop", prompt)
        self.assertIn("ALTERNATE THEM: hero, fact", prompt)
        self.assertIn("Never write \"the main character\" in a fact scene", prompt)


@override_settings(GEMINI_API_KEY="k", GEMINI_TEXT_MODEL="m")
class GenerateScriptTaskTests(TestCase):
    def setUp(self):
        self.p = Project.objects.create(topic="Why Do We Have Nightmares?", target_duration_sec=64, seconds_per_image=8,
                                        niche=Niche.active())

    def fake_json(self, status="warning", scenes=8):
        def _f(prompt, schema, **kw):
            if schema is sc.ScriptOut:
                return make_script(scenes)
            if schema is director.DirectionOut:
                return fake_directions(scenes)
            return compliance.ComplianceResult(findings=[
                compliance.Finding(category="Reklama", status="pass", message="ok"),
                compliance.Finding(category="O'ziga xoslik", status=status, message="shaxsiy fikr qo'shing"),
            ])
        return _f

    def test_script_saved_and_stops_for_review(self):
        with mock.patch.object(gemini_client, "generate_json", side_effect=self.fake_json()):
            tasks.generate_script(self.p.pk)
        self.p.refresh_from_db()
        self.assertEqual(self.p.status, Project.Status.SCRIPT_READY)
        self.assertEqual(self.p.scenes.count(), 8)
        self.assertEqual(self.p.scenes.get(order=1).beat_type, "hook")
        s3 = self.p.scenes.get(order=3)
        self.assertEqual([x["tag"] for x in s3.sfx], ["ding"])  # the director's choice replaced the script's cue
        self.assertEqual(self.p.scenes.get(order=5).on_screen_text, "9 MIN")
        emotions = list(self.p.scenes.order_by("order").values_list("emotion", flat=True))
        self.assertEqual(emotions[3], "neutral")  # 4th "curious" in a row was broken up
        self.assertEqual(self.p.title, "Why Do We Have Nightmares?")
        self.assertEqual(self.p.script_json["mood"], "mysterious")
        self.assertEqual(ComplianceCheck.objects.get(project=self.p).status, "warning")
        self.assertFalse(self.p.is_working)

    def test_auto_approve_on_warning_but_not_on_fail(self):
        self.p.auto_approve = True
        self.p.save()
        with mock.patch.object(gemini_client, "generate_json", side_effect=self.fake_json("warning")):
            tasks.generate_script(self.p.pk)
        self.p.refresh_from_db()
        self.assertEqual(self.p.status, Project.Status.APPROVED)
        q = Project.objects.create(topic="Other topic entirely", target_duration_sec=64, auto_approve=True)
        with mock.patch.object(gemini_client, "generate_json", side_effect=self.fake_json("fail")):
            tasks.generate_script(q.pk)
        q.refresh_from_db()
        self.assertEqual(q.status, Project.Status.SCRIPT_READY)  # fail forces a manual stop

    def test_wrong_scene_count_retries_once(self):
        calls = []

        def f(prompt, schema, **kw):
            calls.append(schema)
            if schema is sc.ScriptOut:
                return make_script(3 if len(calls) == 1 else 8)
            return compliance.ComplianceResult(findings=[])
        with mock.patch.object(gemini_client, "generate_json", side_effect=f):
            tasks.generate_script(self.p.pk)
        self.assertEqual(calls.count(sc.ScriptOut), 2)
        self.assertEqual(self.p.scenes.count(), 8)

    def test_poor_alternation_asks_again(self):
        prompts = []

        def f(prompt, schema, **kw):
            if schema is sc.ScriptOut:
                prompts.append(prompt)
                return make_script(8, alternate=len(prompts) > 1)
            if schema is director.DirectionOut:
                return fake_directions(8)
            return compliance.ComplianceResult(findings=[])
        with mock.patch.object(gemini_client, "generate_json", side_effect=f):
            tasks.generate_script(self.p.pk)
        self.assertEqual(len(prompts), 2)
        self.assertIn("Strictly alternate", prompts[1])
        kinds = [s.get("scene_kind") for s in Project.objects.get(pk=self.p.pk).script_json["scenes"]]
        self.assertEqual(kinds, ["hero", "fact"] * 4)

    def test_gemini_error_marks_failed(self):
        with mock.patch.object(gemini_client, "generate_json", side_effect=gemini_client.GeminiError("Model topilmadi")):
            tasks.generate_script(self.p.pk)
        self.p.refresh_from_db()
        self.assertEqual(self.p.status, Project.Status.FAILED)
        self.assertIn("Model topilmadi", self.p.error_message)
        self.assertFalse(self.p.is_working)

