import shutil
import tempfile
from datetime import timedelta
from unittest import mock

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from pydantic import BaseModel

from apps.videos.models import (
    ChannelSource, ChannelVideo, ComplianceRule, MusicTrack, Niche, PolicyChangeNote, PolicyDocument, Project,
    SoundEffect, SuggestedTopic,
)
from apps.videos.services import channel_research as cr
from apps.videos.services import compliance, gemini_client, media_library as lib, policy_watch

TMP_MEDIA = tempfile.mkdtemp(prefix="ae-test-media-")


def tearDownModule():
    shutil.rmtree(TMP_MEDIA, ignore_errors=True)


# ------------------------------------------------------------------ pure helpers
class HelperTests(TestCase):
    def test_parse_channel_input(self):
        self.assertEqual(cr.parse_channel_input("https://www.youtube.com/@Inkexplainer96"), {"handle": "@Inkexplainer96"})
        self.assertEqual(cr.parse_channel_input("@ink.explainer"), {"handle": "@ink.explainer"})
        self.assertEqual(cr.parse_channel_input("https://youtube.com/channel/UCpgrEMx8diLrw7YNQ6r3uUw"),
                         {"id": "UCpgrEMx8diLrw7YNQ6r3uUw"})
        self.assertEqual(cr.parse_channel_input("https://www.youtube.com/user/someone"), {"username": "someone"})
        with self.assertRaises(cr.YouTubeError):
            cr.parse_channel_input("https://example.com/not a channel!")

    def test_parse_iso_duration(self):
        self.assertEqual(cr.parse_iso_duration("PT11M13S"), 673)
        self.assertEqual(cr.parse_iso_duration("PT1H2M3S"), 3723)
        self.assertEqual(cr.parse_iso_duration("P1DT1S"), 86401)
        self.assertEqual(cr.parse_iso_duration("bogus"), 0)

    def test_worst_status_and_auto_approve(self):
        self.assertEqual(compliance.worst_status([]), "pass")
        self.assertEqual(compliance.worst_status(["pass", "warning", "pass"]), "warning")
        self.assertEqual(compliance.worst_status(["warning", "fail", "pass"]), "fail")
        self.assertEqual(compliance.worst_status(["PASS", "weird"]), "warning")
        self.assertTrue(compliance.can_auto_approve("warning"))
        self.assertFalse(compliance.can_auto_approve("fail"))

    def test_keyword_tags(self):
        self.assertEqual(lib.keyword_tags("Big_Whoosh-Transition 02.wav", ["whoosh", "pop"]), ["whoosh"])
        self.assertEqual(lib.keyword_tags("Mysterious Dark Piano.mp3", ["mysterious", "sad", "calm"]), ["mysterious", "sad"])
        self.assertEqual(lib.parse_tags(" Calm, calm ;Epic,, "), ["calm", "epic"])

    def test_clean_text_strips_boilerplate(self):
        html = ("<html><body><nav>Menu Home</nav><header>Top</header><article><h1>Monetization policies</h1>"
                "<p>Rule one about reused content.</p><p>Was this helpful?</p></article><footer>Footer</footer>"
                "<script>var x=1</script></body></html>")
        text = policy_watch.clean_text(html)
        self.assertIn("Rule one about reused content.", text)
        for junk in ("Menu", "Footer", "var x", "Was this helpful?"):
            self.assertNotIn(junk, text)

    def test_niche_brief(self):
        n = Niche.active()
        self.assertIsNotNone(n)  # seeded by migration
        brief = n.prompt_brief()
        self.assertIn("Niche:", brief)
        self.assertIn("Avoid:", brief)
        p = Project.objects.create(topic="x", niche=n)
        self.assertEqual(n.character_description, p.character_description)
        self.assertNotIn(n.character_description, p.effective_style_guide)


# ------------------------------------------------------------------ YouTube import + Gemini (mocked)
def yt_response(path, params):
    if path.endswith("/channels"):
        return {"items": [{"id": "UCabcdefghijklmnopqrstuv", "snippet": {"title": "Ink Explainer", "customUrl": "@ink",
                "description": "desc", "thumbnails": {"medium": {"url": "https://x/y.jpg"}}},
                "statistics": {"subscriberCount": "100000", "viewCount": "14959116", "videoCount": "2"},
                "contentDetails": {"relatedPlaylists": {"uploads": "UUabc"}}}]}
    if path.endswith("/playlistItems"):
        return {"items": [{"contentDetails": {"videoId": "v1"}}, {"contentDetails": {"videoId": "v2"}}]}
    if path.endswith("/videos"):
        return {"items": [
            {"id": "v1", "snippet": {"title": "What Did Ancient Humans Actually Do All Day?", "publishedAt": "2026-08-21T10:00:00Z",
             "thumbnails": {"high": {"url": "https://i/1.jpg"}}}, "statistics": {"viewCount": "8744094", "likeCount": "47685"},
             "contentDetails": {"duration": "PT11M13S"}},
            {"id": "v2", "snippet": {"title": "What is The IKEA Effect.", "publishedAt": "2026-04-28T10:00:00Z"},
             "statistics": {"viewCount": "14665"}, "contentDetails": {"duration": "PT4M9S"}},
        ]}
    raise AssertionError(path)


def fake_get(url, params=None, timeout=None):
    r = mock.Mock(status_code=200)
    r.json.return_value = yt_response(url, params)
    return r


@override_settings(YOUTUBE_API_KEY="yt-key", GEMINI_API_KEY="g-key", GEMINI_TEXT_MODEL="gemini-test", MEDIA_ROOT=TMP_MEDIA)
class ChannelResearchTests(TestCase):
    def setUp(self):
        self.ch = ChannelSource.objects.create(name="x", handle_or_url="https://www.youtube.com/@Inkexplainer96", niche=Niche.active())

    @mock.patch("apps.videos.services.channel_research.requests.get", side_effect=fake_get)
    def test_import_channel(self, _get):
        self.assertEqual(cr.import_channel(self.ch), 2)
        self.ch.refresh_from_db()
        self.assertEqual(self.ch.name, "Ink Explainer")
        self.assertEqual(self.ch.subscriber_count, 100000)
        v = ChannelVideo.objects.get(youtube_id="v1")
        self.assertEqual(v.duration_sec, 673)
        self.assertEqual(v.view_count, 8744094)
        self.assertEqual(cr.import_channel(self.ch), 2)  # idempotent
        self.assertEqual(ChannelVideo.objects.count(), 2)

    @mock.patch("apps.videos.services.channel_research.requests.get")
    def test_quota_error_message(self, get):
        get.return_value = mock.Mock(status_code=403)
        get.return_value.json.return_value = {"error": {"errors": [{"reason": "quotaExceeded"}]}}
        with self.assertRaisesMessage(cr.YouTubeError, "limiti tugadi"):
            cr.import_channel(self.ch)

    @mock.patch("apps.videos.services.channel_research.requests.get", side_effect=fake_get)
    def test_suggestions_skip_duplicates(self, _get):
        cr.import_channel(self.ch)
        Project.objects.create(topic="How Did Ancient Humans Brush Their Teeth?")
        ideas = cr.TopicIdeas(ideas=[
            cr.TopicIdea(topic="What Did Ancient Humans Actually Do All Day", rationale="dup of channel"),
            cr.TopicIdea(topic="How did ancient humans brush their teeth", rationale="dup of mine"),
            cr.TopicIdea(topic="How Did Ancient Humans Know What Time It Was?", rationale="yangi"),
            cr.TopicIdea(topic="What Did Ancient Humans Do When They Couldn't Sleep?", rationale="yangi"),
        ])
        with mock.patch.object(gemini_client, "generate_json", return_value=ideas):
            created = cr.suggest_topics(self.ch, count=10)
        self.assertEqual([s.topic_text for s in created], [
            "How Did Ancient Humans Know What Time It Was?", "What Did Ancient Humans Do When They Couldn't Sleep?"])

    @mock.patch("apps.videos.services.channel_research.requests.get", side_effect=fake_get)
    def test_task_end_to_end(self, _get):
        from apps.videos import tasks

        notes = cr.StyleNotes(topic_formula="A", title_style="B", tone="C", typical_length="D", what_performs_best="E",
                              what_underperforms="F", thumbnail_notes="G", advice_for_original_channel="H")

        def fake_json(prompt, schema, **kw):
            return notes if schema is cr.StyleNotes else cr.TopicIdeas(ideas=[cr.TopicIdea(topic="Why Did Ancient Humans Dance?", rationale="r")])

        with mock.patch.object(gemini_client, "generate_json", side_effect=fake_json):
            tasks.channel_research(self.ch.pk)
        self.ch.refresh_from_db()
        self.assertEqual(self.ch.state, ChannelSource.State.READY)
        self.assertIn("Mavzu formulasi: A", self.ch.style_notes)
        self.assertEqual(self.ch.suggestions.count(), 1)

    def test_task_records_failure(self):
        from apps.videos import tasks

        with override_settings(YOUTUBE_API_KEY=""):
            tasks.channel_research(self.ch.pk)
        self.ch.refresh_from_db()
        self.assertEqual(self.ch.state, ChannelSource.State.FAILED)
        self.assertIn("YOUTUBE_API_KEY", self.ch.error_message)


# ------------------------------------------------------------------ Gemini client
class GeminiClientTests(TestCase):
    class Out(BaseModel):
        x: int

    @override_settings(GEMINI_API_KEY="k", GEMINI_TEXT_MODEL="m")
    def test_json_retry_on_invalid_then_ok(self):
        client = mock.Mock()
        bad = mock.Mock(parsed=None, text="not json")
        good = mock.Mock(parsed=None, text='```json\n{"x": 5}\n```')
        client.models.generate_content.side_effect = [bad, good]
        with mock.patch.object(gemini_client, "get_client", return_value=client):
            self.assertEqual(gemini_client.generate_json("p", self.Out).x, 5)
        self.assertEqual(client.models.generate_content.call_count, 2)

    @override_settings(GEMINI_API_KEY="k", GEMINI_TEXT_MODEL="m")
    def test_backoff_on_429(self):
        from google.genai import errors

        client = mock.Mock()
        client.models.generate_content.side_effect = [
            errors.APIError(429, {"error": {"message": "quota", "status": "RESOURCE_EXHAUSTED"}}),
            mock.Mock(parsed=self.Out(x=1), text='{"x":1}'),
        ]
        with mock.patch.object(gemini_client, "get_client", return_value=client), mock.patch("time.sleep"):
            self.assertEqual(gemini_client.generate_json("p", self.Out).x, 1)

    @override_settings(GEMINI_API_KEY="", GEMINI_TEXT_MODEL="")
    def test_not_configured(self):
        self.assertFalse(gemini_client.is_configured())
        with self.assertRaises(gemini_client.GeminiNotConfigured):
            gemini_client.generate_text("hi")


# ------------------------------------------------------------------ library
@override_settings(MEDIA_ROOT=TMP_MEDIA, GEMINI_API_KEY="")
class LibraryTests(TestCase):
    def track(self, title, tags):
        return MusicTrack.objects.create(title=title, mood_tags=tags, file=ContentFile(b"x", name=f"{title}.mp3"))

    def test_pick_music_mood_then_least_recently_used(self):
        a, b = self.track("A", ["mysterious"]), self.track("B", ["mysterious", "calm"])
        c = self.track("C", ["playful"])
        self.assertEqual(lib.pick_music("mysterious"), a)  # never used, lowest pk
        p1 = Project.objects.create(topic="t1", music_track=a)
        self.assertEqual(lib.pick_music("mysterious"), b)
        p2 = Project.objects.create(topic="t2", music_track=b)
        Project.objects.filter(pk=p1.pk).update(created_at=timezone.now() - timedelta(days=5))
        Project.objects.filter(pk=p2.pk).update(created_at=timezone.now() - timedelta(days=1))
        self.assertEqual(lib.pick_music("mysterious"), a)  # a used longest ago
        self.assertEqual(lib.pick_music("epic"), c)  # no match -> any track (c never used)

    def test_pick_sfx_rotation_and_missing(self):
        s1 = SoundEffect.objects.create(name="w1", tags=["whoosh"], file=ContentFile(b"x", name="w1.wav"))
        s2 = SoundEffect.objects.create(name="w2", tags=["Whoosh", "swoosh"], file=ContentFile(b"x", name="w2.wav"))
        self.assertEqual(lib.pick_sfx("whoosh", seed=0), s1)
        self.assertEqual(lib.pick_sfx("whoosh", seed=1), s2)
        self.assertIsNone(lib.pick_sfx("riser"))
        self.assertIsNone(lib.pick_sfx(None))
        self.assertIn("riser", lib.missing_sfx_tags())
        self.assertNotIn("swoosh", lib.missing_sfx_tags())

    def test_starter_pack_import(self):
        m, s = lib.import_starter_pack()
        self.assertGreaterEqual(m, 10)
        self.assertGreaterEqual(s, 20)
        self.assertEqual(lib.import_starter_pack(), (0, 0))  # idempotent
        self.assertEqual(lib.missing_sfx_tags(), [])
        self.assertTrue(all(t.duration > 30 for t in MusicTrack.objects.all()))
        self.assertTrue(all(0 < x.duration < 5 for x in SoundEffect.objects.all()))
        self.assertIsNotNone(lib.pick_music("mysterious"))

    def test_upload_view_with_auto_tags(self):
        from pathlib import Path

        wav = (Path(lib.STARTER_DIR) / "sfx" / "whoosh_01.wav").read_bytes()
        r = self.client.post(reverse("videos:library"), {
            "tab": "sfx", "files": [SimpleUploadedFile("my_whoosh_fast.wav", wav, content_type="audio/wav")]})
        self.assertEqual(r.status_code, 302)
        sfx = SoundEffect.objects.get()
        self.assertEqual(sfx.tags, ["whoosh"])
        self.assertGreater(sfx.duration, 0.3)
        r = self.client.post(reverse("videos:library_tags", args=["sfx", sfx.pk]), {"tags": "pop, click", "title": "New"})
        self.assertContains(r, "New")
        sfx.refresh_from_db()
        self.assertEqual(sfx.tags, ["click", "pop"])
        self.client.post(reverse("videos:library_delete", args=["sfx", sfx.pk]))
        self.assertFalse(SoundEffect.objects.exists())

    def test_rejects_non_audio(self):
        r = self.client.post(reverse("videos:library"), {"tab": "music", "files": [SimpleUploadedFile("x.exe", b"MZ")]})
        self.assertContains(r, "Audio emas")


# ------------------------------------------------------------------ policy watch
@override_settings(GEMINI_API_KEY="")
class PolicyWatchTests(TestCase):
    def setUp(self):
        self.doc = PolicyDocument.objects.first()  # seeded

    def test_first_same_changed_error(self):
        base = "Monetization rules.\n" * 50
        with mock.patch.object(policy_watch, "fetch_text", return_value=base):
            self.assertEqual(policy_watch.check_document(self.doc), "first")
            self.assertEqual(policy_watch.check_document(self.doc), "same")
        self.assertFalse(PolicyChangeNote.objects.exists())
        with mock.patch.object(policy_watch, "fetch_text", return_value=base + "New rule about AI voices.\n"):
            self.assertEqual(policy_watch.check_document(self.doc), "changed")
        note = PolicyChangeNote.objects.get()
        self.assertIn("+New rule about AI voices.", note.plain_summary)
        self.assertFalse(note.reviewed)
        with mock.patch.object(policy_watch, "fetch_text", side_effect=policy_watch.PolicyFetchError("JS page")):
            self.assertEqual(policy_watch.check_document(self.doc), "error")
        self.doc.refresh_from_db()
        self.assertFalse(self.doc.last_check_ok)  # a failed check is NOT "no changes"
        self.assertEqual(PolicyChangeNote.objects.count(), 1)

    def test_short_page_is_an_error(self):
        resp = mock.Mock(status_code=200, text="<html><body><div id=app></div></body></html>")
        with mock.patch("apps.videos.services.policy_watch.requests.get", return_value=resp):
            with self.assertRaises(policy_watch.PolicyFetchError):
                policy_watch.fetch_text("https://x")

    def test_banner_and_review(self):
        PolicyChangeNote.objects.create(policy_document=self.doc, plain_summary="s")
        r = self.client.get(reverse("videos:home"))
        self.assertContains(r, "ko'rib chiqilmagan")
        self.client.post(reverse("videos:policy_notes_review_all"))
        self.assertNotContains(self.client.get(reverse("videos:home")), "ko'rib chiqilmagan")

    def test_schedule_registered(self):
        from django_q.models import Schedule

        policy_watch.ensure_schedule()
        s = Schedule.objects.get(name="policy-watch")
        self.assertEqual(s.func, "apps.videos.tasks.policy_check_all")


# ------------------------------------------------------------------ pages
@override_settings(MEDIA_ROOT=TMP_MEDIA)
class PageTests(TestCase):
    def test_all_pages_render(self):
        ch = ChannelSource.objects.create(name="Ink", handle_or_url="@ink", niche=Niche.active(), style_notes="Ohang: kulgili")
        v = ChannelVideo.objects.create(channel=ch, youtube_id="abc", title="Video", view_count=10, duration_sec=61)
        SuggestedTopic.objects.create(channel=ch, topic_text="Topic A", rationale="r")
        p = Project.objects.create(topic="Watch me", niche=Niche.active())
        for name, args in [("home", []), ("project_list", []), ("project_detail", [p.pk]), ("watch", []),
                           ("watch_project", [p.pk]), ("watch_reference", [v.pk]), ("niche", []), ("channels", []),
                           ("channel_detail", [ch.pk]), ("channel_status", [ch.pk]), ("library", []), ("policy", [])]:
            r = self.client.get(reverse(f"videos:{name}", args=args))
            self.assertEqual(r.status_code, 200, name)
        self.assertContains(self.client.get(reverse("videos:channel_detail", args=[ch.pk])), "Topic A")
        self.assertContains(self.client.get(reverse("videos:watch_reference", args=[v.pk])), "youtube-nocookie.com/embed/abc")

    def test_niche_save(self):
        n = Niche.active()
        data = {f: getattr(n, f) for f in ["name", "name_en", "description", "audience", "tone", "title_formula",
                "content_pillars", "avoid_topics", "originality_rules", "style_guide", "character_description",
                "default_minutes", "default_seconds_per_image", "default_mood"]}
        data["name"] = "Yangi nom"
        r = self.client.post(reverse("videos:niche"), data)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Niche.active().name, "Yangi nom")

    def test_new_project_gets_niche_and_defaults(self):
        n = Niche.active()
        r = self.client.get(reverse("videos:home"))
        self.assertContains(r, f'value="{int(n.default_minutes)}')
        self.client.post(reverse("videos:home"), {"topic": "Why Did Ancient Humans Paint Caves?", "target_minutes": 9,
                                                  "seconds_per_image": 8, "tts_provider": "edge"})
        self.assertEqual(Project.objects.get().niche, n)

    @override_settings(YOUTUBE_API_KEY="k")
    def test_add_channel_enqueues(self):
        with mock.patch("django_q.tasks.async_task") as at:
            r = self.client.post(reverse("videos:channels"), {"url": "https://www.youtube.com/@Inkexplainer96"})
        ch = ChannelSource.objects.get()
        self.assertRedirects(r, reverse("videos:channel_detail", args=[ch.pk]))
        self.assertEqual(at.call_args.args[0], "apps.videos.tasks.channel_research")
        r = self.client.post(reverse("videos:channels"), {"url": "https://www.youtube.com/@Inkexplainer96"})
        self.assertContains(r, "allaqachon")

    @override_settings(YOUTUBE_API_KEY="")
    def test_add_channel_without_key(self):
        r = self.client.post(reverse("videos:channels"), {"url": "@Inkexplainer96"}, follow=True)
        self.assertContains(r, "YOUTUBE_API_KEY")
        self.assertFalse(ChannelSource.objects.exists())

    def test_policy_doc_and_rule_crud(self):
        with mock.patch("django_q.tasks.async_task"):
            self.client.post(reverse("videos:policy_doc_save"), {"doc-label": "Test", "doc-url": "https://example.com/p"})
        d = PolicyDocument.objects.get(label="Test")
        self.client.post(reverse("videos:policy_doc_toggle", args=[d.pk]))
        d.refresh_from_db()
        self.assertFalse(d.enabled)
        n = ComplianceRule.objects.count()
        self.client.post(reverse("videos:policy_rule_save"), {"rule-title": "Yangi", "rule-instruction": "Check X", "rule-enabled": "on"})
        self.assertEqual(ComplianceRule.objects.count(), n + 1)
        r = ComplianceRule.objects.get(title="Yangi")
        self.client.post(reverse("videos:policy_rule_save"), {"pk": r.pk, "rule-title": "Yangi", "rule-instruction": "Check X"})
        r.refresh_from_db()
        self.assertFalse(r.enabled)
        self.client.post(reverse("videos:policy_rule_save"), {"pk": r.pk, "delete": "1"})
        self.assertEqual(ComplianceRule.objects.count(), n)


@override_settings(GEMINI_API_KEY="k", GEMINI_TEXT_MODEL="main-model", GEMINI_FALLBACK_MODELS="lite-model, bad-model")
class GeminiFallbackTests(TestCase):
    class Out(BaseModel):
        x: int

    def busy(self):
        from google.genai import errors
        return errors.APIError(503, {"error": {"message": "This model is currently experiencing high demand.", "status": "UNAVAILABLE"}})

    def test_busy_main_model_falls_back(self):
        client = mock.Mock()
        used = []

        def gen(model, contents, config):
            used.append(model)
            if model == "main-model":
                raise self.busy()
            return mock.Mock(parsed=self.Out(x=7), text='{"x":7}')
        client.models.generate_content.side_effect = gen
        with mock.patch.object(gemini_client, "get_client", return_value=client), mock.patch("time.sleep"):
            self.assertEqual(gemini_client.generate_json("p", self.Out).x, 7)
        self.assertEqual(used.count("main-model"), 5)
        self.assertEqual(used[-1], "lite-model")

    def test_all_busy_gives_clear_message(self):
        from google.genai import errors

        client = mock.Mock()

        def gen(model, contents, config):
            if model == "bad-model":
                raise errors.APIError(404, {"error": {"message": "not found", "status": "NOT_FOUND"}})
            raise self.busy()
        client.models.generate_content.side_effect = gen
        with mock.patch.object(gemini_client, "get_client", return_value=client), mock.patch("time.sleep"):
            with self.assertRaisesMessage(gemini_client.GeminiError, "Barcha modellar band"):
                gemini_client.generate_text("p")

    def test_bad_main_key_is_not_masked(self):
        from google.genai import errors

        client = mock.Mock()
        client.models.generate_content.side_effect = errors.APIError(400, {"error": {"message": "API key not valid", "status": "INVALID_ARGUMENT"}})
        with mock.patch.object(gemini_client, "get_client", return_value=client):
            with self.assertRaisesMessage(gemini_client.GeminiError, "GEMINI_API_KEY"):
                gemini_client.generate_text("p")


class ManualSuggestionTests(TestCase):
    def test_add_shows_on_home_and_creates_project(self):
        from django.urls import reverse

        from apps.videos.models import Project, SuggestedTopic

        r = self.client.post(reverse("videos:suggestion_add"),
                             {"topic_text": "  Why did ancient people   fear eclipses? ", "rationale": "Kuzatuvchilar so'radi"})
        self.assertRedirects(r, reverse("videos:home"))
        s = SuggestedTopic.objects.get()
        self.assertEqual(s.topic_text, "Why did ancient people fear eclipses?")
        self.assertTrue(s.is_manual)
        page = self.client.get(reverse("videos:home")).content.decode()
        self.assertIn("Why did ancient people fear eclipses?", page)
        self.assertIn("Qo'lda qo'shilgan", page)
        self.assertIn(reverse("videos:suggestion_add"), page)
        # duplicate is refused
        self.client.post(reverse("videos:suggestion_add"), {"topic_text": "why did ancient people fear eclipses"})
        self.assertEqual(SuggestedTopic.objects.count(), 1)
        # empty / too short is refused
        self.client.post(reverse("videos:suggestion_add"), {"topic_text": "ab"})
        self.assertEqual(SuggestedTopic.objects.count(), 1)
        # "create this video" -> project linked, suggestion used, pages render without a channel
        form = self.client.get(reverse("videos:home") + f"?suggestion={s.pk}").content.decode()
        self.assertIn('value="Why did ancient people fear eclipses?"', form)
        r = self.client.post(reverse("videos:home"), {"topic": s.topic_text, "source_suggestion": s.pk,
                                                      "target_minutes": 3, "seconds_per_image": 8,
                                                      "tts_provider": "edge", "confirm_duplicate": "on"})
        p = Project.objects.get()
        self.assertEqual(p.source_suggestion, s)
        s.refresh_from_db()
        self.assertEqual(s.status, SuggestedTopic.Status.USED)
        self.assertContains(self.client.get(reverse("videos:project_detail", args=[p.pk])), "qo'lda qo'shilgan")
        self.assertContains(self.client.get(reverse("videos:project_list")), "qo'lda qo'shilgan")

    def test_dismiss_manual_goes_home(self):
        from django.urls import reverse

        from apps.videos.models import SuggestedTopic

        s = SuggestedTopic.objects.create(topic_text="Hand made idea")
        r = self.client.post(reverse("videos:suggestion_dismiss", args=[s.pk]))
        self.assertRedirects(r, reverse("videos:home"))
        s.refresh_from_db()
        self.assertEqual(s.status, SuggestedTopic.Status.DISMISSED)
