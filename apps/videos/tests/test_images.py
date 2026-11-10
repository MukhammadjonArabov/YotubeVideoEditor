import base64
import io
from unittest import mock

from django.test import TestCase, override_settings
from PIL import Image

from apps.videos import tasks
from apps.videos.models import Project, Scene
from apps.videos.services import scenes as ops
from apps.videos.services.image_providers import (
    CloudflareImageProvider, ImageProviderError, ImageProviderNotConfigured, get_provider, provider_status,
)
from apps.videos.services.images import build_prompt, generate_scene_image


def fake_png(size=(1024, 1024), colour="orange") -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, colour).save(buf, "JPEG")
    return buf.getvalue()


def resp(status=200, json_body=None, content=b"", ctype="application/json"):
    r = mock.Mock()
    r.status_code = status
    r.headers = {"Content-Type": ctype}
    r.content = content
    r.json.return_value = json_body or {}
    return r


CF = dict(CLOUDFLARE_ACCOUNT_ID="acc123", CLOUDFLARE_API_TOKEN="tok", IMAGE_PROVIDER="cloudflare",
          CLOUDFLARE_IMAGE_MODEL="@cf/black-forest-labs/flux-1-schnell", CLOUDFLARE_IMAGE_STEPS=4)


class CloudflareProviderTests(TestCase):
    def provider(self):
        return CloudflareImageProvider("acc123", "tok", "@cf/black-forest-labs/flux-1-schnell", steps=12, backoff_base=0)

    def test_url_and_payload(self):
        p = self.provider()
        self.assertEqual(p.url, "https://api.cloudflare.com/client/v4/accounts/acc123/ai/run/@cf/black-forest-labs/flux-1-schnell")
        payload = p.build_payload("x" * 3000, seed=5)
        self.assertEqual(payload["steps"], 8)  # clamped to the model maximum
        self.assertEqual(len(payload["prompt"]), 2048)
        self.assertNotIn("seed", payload)  # flux-1-schnell refuses a seed (verified against the real API)
        other = CloudflareImageProvider("a", "t", "@cf/some/other-model")
        self.assertEqual(other.build_payload("p", seed=5)["seed"], 5)

    @mock.patch("apps.videos.services.image_providers.cloudflare.requests.post")
    def test_seed_dropped_when_model_refuses_it(self, post):
        img = fake_png()
        post.side_effect = [
            resp(400, json_body={"errors": [{"message": "Additional or unevaluated properties '/seed' not allowed"}]}),
            resp(json_body={"result": {"image": base64.b64encode(img).decode()}}),
        ]
        p = CloudflareImageProvider("a", "t", "@cf/some/other-model", backoff_base=0)
        self.assertEqual(p.generate("cat", seed=7), img)
        self.assertNotIn("seed", post.call_args_list[1].kwargs["json"])

    @mock.patch("apps.videos.services.image_providers.cloudflare.requests.post")
    def test_success_decodes_base64(self, post):
        img = fake_png()
        post.return_value = resp(json_body={"success": True, "result": {"image": base64.b64encode(img).decode()}})
        self.assertEqual(self.provider().generate("cat"), img)
        _, kwargs = post.call_args
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer tok")

    @mock.patch("apps.videos.services.image_providers.cloudflare.requests.post")
    def test_retries_on_429_then_succeeds(self, post):
        img = fake_png()
        post.side_effect = [resp(429), resp(503),
                            resp(json_body={"result": {"image": base64.b64encode(img).decode()}})]
        self.assertEqual(self.provider().generate("cat"), img)
        self.assertEqual(post.call_count, 3)

    @mock.patch("apps.videos.services.image_providers.cloudflare.requests.post")
    def test_auth_error_is_not_retried(self, post):
        post.return_value = resp(401, json_body={"errors": [{"message": "Authentication error"}]})
        with self.assertRaisesMessage(ImageProviderError, "Token noto'g'ri"):
            self.provider().generate("cat")
        self.assertEqual(post.call_count, 1)

    @override_settings(CLOUDFLARE_ACCOUNT_ID="", CLOUDFLARE_API_TOKEN="", IMAGE_PROVIDER="cloudflare")
    def test_not_configured(self):
        with self.assertRaises(ImageProviderNotConfigured):
            get_provider()
        self.assertFalse(provider_status()[0])


class FakeProvider:
    name = "fake"
    supports_reference = False

    def __init__(self, fail_on=()):
        self.calls = []
        self.refs = []
        self.fail_on = fail_on

    def generate(self, prompt, seed=None, references=None):
        self.calls.append((prompt, seed))
        self.refs.append(references)
        if any(f in prompt for f in self.fail_on):
            raise ImageProviderError("boom")
        return fake_png()


class GenerateImagesTests(TestCase):
    def setUp(self):
        self.p = Project.objects.create(topic="Images topic", style_guide="STYLE")
        self.a = ops.add_scene(self.p, narration="a", image_prompt="a caveman")
        self.b = ops.add_scene(self.p, narration="b", image_prompt="a mammoth")
        self.c = ops.add_scene(self.p, narration="c", image_prompt="")

    def tearDown(self):
        for s in self.p.scenes.all():
            if s.image:
                s.image.delete()

    def test_prompt_contains_style_and_scene(self):
        prompt = build_prompt("STYLE", "a caveman.")
        self.assertTrue(prompt.startswith("STYLE. Scene: a caveman."))
        self.assertIn("16:9", prompt)
        self.assertIn("head to feet", prompt)
        self.assertNotIn("MAIN CHARACTER", build_prompt("STYLE", "a caveman.", "round white head"))

    def test_object_scenes_drop_the_stick_figure_style_and_ask_for_no_people(self):
        style = "flat cartoon, stick-figure characters with dot eyes; other people are plain stick figures, clean outlines, 16:9"
        obj = build_prompt(style, "A tooth beside a green leaf on a stone.")
        self.assertNotIn("stick", obj.split("Scene:")[0])
        self.assertIn("clean outlines", obj)
        self.assertIn("no people", obj)
        self.assertNotIn("head to feet", obj)
        people = build_prompt(style, "Four skulls and a group of friends by a fire.")
        self.assertIn("stick-figure characters", people)
        self.assertIn("head to feet", people)
        self.assertNotIn("no people", build_prompt(style, "A Neanderthal sits by the fire."))

    def test_scene_image_saved_as_1080p_and_skip_existing(self):
        fp = FakeProvider()
        self.assertTrue(generate_scene_image(self.a, provider=fp))
        self.a.refresh_from_db()
        self.assertEqual(Image.open(self.a.image.path).size, (1920, 1080))
        self.assertFalse(generate_scene_image(self.a, provider=fp))  # already has one
        self.assertEqual(len(fp.calls), 1)

    def test_locked_image_never_regenerated(self):
        self.a.image_locked = True
        self.a.save()
        self.assertFalse(generate_scene_image(self.a, provider=FakeProvider(), force=True))

    def test_task_draws_missing_and_marks_failures(self):
        fp = FakeProvider(fail_on=("mammoth",))
        Project.objects.filter(pk=self.p.pk).update(is_working=True)
        with mock.patch("apps.videos.services.image_providers.get_provider", return_value=fp):
            tasks.generate_images(self.p.pk)
        self.a.refresh_from_db(); self.b.refresh_from_db(); self.c.refresh_from_db()
        self.assertTrue(self.a.image)
        self.assertEqual(self.b.status, Scene.Status.FAILED)
        self.assertEqual(self.b.error_message, "boom")
        self.assertFalse(self.c.image)  # no prompt -> skipped
        self.p.refresh_from_db()
        self.assertFalse(self.p.is_working)
        self.assertIn("1 ta tayyor", self.p.progress_message)
        self.assertIn("1 ta xato", self.p.progress_message)

    @override_settings(MAX_IMAGES_PER_PROJECT=1)
    def test_hard_cap(self):
        fp = FakeProvider()
        with mock.patch("apps.videos.services.image_providers.get_provider", return_value=fp):
            tasks.generate_images(self.p.pk)
        self.assertEqual(len(fp.calls), 1)


class CharacterConsistencyTests(TestCase):
    CHAR = "round plain white head, spiky brown hair, no beard, brown fur tunic"

    def setUp(self):
        from apps.videos.models import Niche

        self.niche = Niche.objects.create(name="N", character_description=self.CHAR, is_active=False)
        self.p = Project.objects.create(topic="Hero topic", style_guide="STYLE", niche=self.niche)
        self.s = ops.add_scene(self.p, narration="a", image_prompt="the main character runs from a lion")

    def tearDown(self):
        for s in self.p.scenes.all():
            if s.image:
                s.image.delete()
        if self.niche.character_reference:
            self.niche.character_reference.delete()

    def test_character_sheet_inserted_only_when_hero_appears(self):
        pr = build_prompt("STYLE", "the main character runs from a lion", self.CHAR)
        self.assertIn("MAIN CHARACTER (must look exactly the same in every image): " + self.CHAR, pr)
        self.assertIn("Scene: the main character (exactly as described above) runs", pr)
        self.assertLess(pr.index("MAIN CHARACTER"), pr.index("Scene:"))
        self.assertNotIn(self.CHAR, build_prompt("STYLE", "a map of Africa", self.CHAR))

    def test_crop_keeps_top_band(self):
        from apps.videos.services.images import normalize_to_1080p

        img = Image.new("RGB", (1000, 1000), "white")
        img.paste(Image.new("RGB", (1000, 100), "red"), (0, 110))  # a "head" near the top
        out = Image.open(io.BytesIO(normalize_to_1080p(img_bytes(img))))
        self.assertEqual(out.getpixel((960, 5))[:3], (255, 0, 0))  # still visible after crop

    def test_qa_redraws_once_and_flags(self):
        from apps.videos.services.image_qa import QAResult

        fp = FakeProvider()
        with mock.patch("apps.videos.services.image_qa.check_scene_image",
                        side_effect=[QAResult(False, "qahramon boshqacha: beard"), QAResult(True)]) as qa:
            generate_scene_image(self.s, provider=fp)
        self.assertEqual(len(fp.calls), 2)
        self.assertNotEqual(fp.calls[0][1], fp.calls[1][1])  # different seed on the redraw
        self.assertEqual(qa.call_count, 2)
        self.s.refresh_from_db()
        self.assertEqual(self.s.error_message, "")

        with mock.patch("apps.videos.services.image_qa.check_scene_image", return_value=QAResult(False, "bosh kesilib qolgan")):
            generate_scene_image(self.s, provider=fp, force=True)
        self.s.refresh_from_db()
        self.assertTrue(self.s.image)
        self.assertIn("bosh kesilib qolgan", self.s.error_message)
        self.assertEqual(self.s.status, Scene.Status.PENDING)

    def test_no_qa_for_scenes_without_hero(self):
        other = ops.add_scene(self.p, narration="b", image_prompt="a map of Africa")
        fp = FakeProvider()
        with mock.patch("apps.videos.services.image_qa.check_scene_image") as qa:
            generate_scene_image(other, provider=fp)
        qa.assert_not_called()
        self.assertEqual(len(fp.calls), 1)

    def test_reference_passed_to_capable_provider(self):
        from django.core.files.base import ContentFile

        from apps.videos.services.image_qa import QAResult

        self.niche.character_reference.save("c.png", ContentFile(fake_png()), save=True)
        self.p.refresh_from_db()
        fp = FakeProvider()
        fp.supports_reference = True
        with mock.patch("apps.videos.services.image_qa.check_scene_image", return_value=QAResult(True)) as qa:
            generate_scene_image(Scene.objects.get(pk=self.s.pk), provider=fp)
        self.assertEqual(len(fp.refs[0]), 1)
        self.assertIsNotNone(qa.call_args.args[3])  # reference goes to the vision check too

    def test_qa_is_skipped_without_gemini(self):
        from apps.videos.services.image_qa import check_scene_image

        with override_settings(GEMINI_API_KEY="", GEMINI_TEXT_MODEL=""):
            self.assertFalse(check_scene_image(fake_png(), self.CHAR, "x").checked)

    def test_qa_parses_gemini_answer(self):
        from apps.videos.services.image_qa import QAOut, check_scene_image

        bad = QAOut(main_character_present=True, matches_character=False, heads_cut_off=True, problems="has a beard")
        with override_settings(GEMINI_ENABLED=True, GEMINI_API_KEY="k", GEMINI_TEXT_MODEL="m"), \
                mock.patch("apps.videos.services.gemini_client.generate_json", return_value=bad) as gj:
            r = check_scene_image(fake_png(), self.CHAR, "x", reference=fake_png())
        self.assertFalse(r.ok)
        self.assertIn("bosh kesilib", r.reason)
        self.assertIn("has a beard", r.reason)
        self.assertEqual(len(gj.call_args.kwargs["images"]), 2)



def img_bytes(img):
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


class AutoInstallTests(TestCase):
    def test_installs_missing_module_once(self):
        from apps.videos.services import autoinstall

        autoinstall._tried.clear()
        with mock.patch("apps.videos.services.autoinstall.subprocess.run") as run:
            self.assertFalse(autoinstall.ensure_module("surely_missing_mod_xyz", "surely-missing==1"))
            self.assertFalse(autoinstall.ensure_module("surely_missing_mod_xyz", "surely-missing==1"))
        self.assertEqual(run.call_count, 1)
        self.assertIn("surely-missing==1", run.call_args.args[0])
        self.assertTrue(autoinstall.ensure_module("json", "x"))


class NamedFake(FakeProvider):
    def __init__(self, name, error=None):
        super().__init__()
        self.name = name
        self.error = error

    def generate(self, prompt, seed=None, references=None):
        self.calls.append((prompt, seed))
        if self.error:
            raise ImageProviderError(self.error)
        return fake_png()


class FallbackChainTests(TestCase):
    def test_switches_after_quota_and_stays_switched(self):
        from apps.videos.services.image_providers import FallbackImageProvider

        cf = NamedFake("cloudflare", "Cloudflare kunlik bepul limiti tugadi")
        po = NamedFake("backup")
        chain = FallbackImageProvider([cf, po])
        chain.generate("a"); chain.generate("b")
        self.assertEqual(len(cf.calls), 1)  # not asked again once its quota is over
        self.assertEqual(len(po.calls), 2)
        self.assertIn("backup bilan davom etildi", chain.notice)

    def test_other_error_only_skips_this_image(self):
        from apps.videos.services.image_providers import FallbackImageProvider

        cf = NamedFake("cloudflare", "So'rov noto'g'ri")
        chain = FallbackImageProvider([cf, NamedFake("backup")])
        chain.generate("a"); chain.generate("b")
        self.assertEqual(len(cf.calls), 2)
        self.assertEqual(chain.notice, "")

    def test_all_fail(self):
        from apps.videos.services.image_providers import FallbackImageProvider

        chain = FallbackImageProvider([NamedFake("cloudflare", "x"), NamedFake("backup", "y")])
        with self.assertRaisesMessage(ImageProviderError, "Cloudflare Workers AI: x | backup: y"):
            chain.generate("a")

    def test_task_reports_switch(self):
        from apps.videos.services.image_providers import FallbackImageProvider

        p = Project.objects.create(topic="Chain", style_guide="S")
        s = ops.add_scene(p, narration="a", image_prompt="a mammoth")
        chain = FallbackImageProvider([NamedFake("cloudflare", "daily limit"), NamedFake("backup")])
        with mock.patch("apps.videos.services.image_providers.get_provider", return_value=chain):
            tasks.generate_images(p.pk)
        p.refresh_from_db(); s.refresh_from_db()
        self.assertTrue(s.image)
        self.assertIn("backup bilan davom etildi", p.progress_message)
        s.image.delete()


class RunwareProviderTests(TestCase):
    def test_not_configured_without_key(self):
        from django.test import override_settings

        from apps.videos.services.image_providers import ImageProviderNotConfigured, RunwareImageProvider

        with override_settings(RUNWARE_API_KEY=""), self.assertRaises(ImageProviderNotConfigured):
            RunwareImageProvider.from_settings()

    def test_request_shape_decode_and_errors(self):
        import base64
        from unittest import mock

        from apps.videos.services.image_providers import ImageProviderError, RunwareImageProvider

        prov = RunwareImageProvider("k", "runware:100@1", steps=4, use_references=True, max_retries=2, backoff_base=0)
        ok = mock.Mock(status_code=200)
        ok.json.return_value = {"data": [{"imageBase64Data": base64.b64encode(b"PNGDATA").decode(), "cost": 0.0006}]}
        with mock.patch("requests.post", return_value=ok) as post:
            data = prov.generate("a cave", seed=5, references=[b"ref"])
        task = post.call_args.kwargs["json"][0]
        self.assertEqual((data, prov.last_cost), (b"PNGDATA", 0.0006))
        self.assertEqual((task["taskType"], task["model"], task["steps"], task["width"] % 64, task["height"] % 64),
                         ("imageInference", "runware:100@1", 4, 0, 0))
        self.assertTrue(task["referenceImages"][0].startswith("data:image/png;base64,"))
        self.assertEqual(post.call_args.kwargs["headers"]["Authorization"], "Bearer k")
        bad = mock.Mock(status_code=401, text="x")
        bad.json.return_value = {"errors": [{"message": "Invalid API key"}]}
        with mock.patch("requests.post", return_value=bad), self.assertRaisesRegex(ImageProviderError, "kaliti"):
            prov.generate("a cave")
        poor = mock.Mock(status_code=200, text="x")
        poor.json.return_value = {"errors": [{"message": "Insufficient credits"}]}
        with mock.patch("requests.post", return_value=poor), self.assertRaisesRegex(ImageProviderError, "limit"):
            prov.generate("a cave")

    def test_model_refusing_seed_is_retried_without_it(self):
        import base64
        from unittest import mock

        from apps.videos.services.image_providers import RunwareImageProvider

        prov = RunwareImageProvider("k", "m", max_retries=3, backoff_base=0)
        refuse = mock.Mock(status_code=400, text="x")
        refuse.json.return_value = {"errors": [{"message": "Unsupported parameter seed"}]}
        ok = mock.Mock(status_code=200)
        ok.json.return_value = {"data": [{"imageBase64Data": base64.b64encode(b"X").decode()}]}
        with mock.patch("requests.post", side_effect=[refuse, ok]) as post:
            self.assertEqual(prov.generate("p", seed=1), b"X")
        self.assertNotIn("seed", post.call_args.kwargs["json"][0])


class ImageCostTests(TestCase):
    def test_runware_cost_is_summed_and_saved_on_the_project(self):
        import base64

        from apps.videos.services.image_providers import RunwareImageProvider, spent

        p = Project.objects.create(topic="Cost", image_model="ideogram:4.5@0")
        prov = RunwareImageProvider("k", "m")
        ok = mock.Mock(status_code=200)
        ok.json.return_value = {"data": [{"imageBase64Data": base64.b64encode(b"X").decode(), "cost": 0.008}]}
        with mock.patch("requests.post", return_value=ok):
            prov.generate("a"), prov.generate("b")
        self.assertEqual(spent(prov), (0.016, 2))
        self.assertAlmostEqual(tasks._add_image_cost(p.pk, prov), 0.016)
        p.refresh_from_db()
        self.assertEqual((round(p.image_cost, 3), p.image_cost_count), (0.016, 2))


class ReplicateProviderTests(TestCase):
    def test_request_result_errors_and_model_routing(self):
        from django.test import override_settings

        from apps.videos.services.image_providers import (FallbackImageProvider, ImageProviderError,
                                                          ReplicateImageProvider, RunwareImageProvider, apply_model)

        prov = ReplicateImageProvider("tok", "black-forest-labs/flux-schnell", max_retries=2, backoff_base=0)
        ok = mock.Mock(status_code=201)
        ok.json.return_value = {"status": "succeeded", "output": ["https://img.example/x.png"]}
        img = mock.Mock(content=b"IMG")
        img.raise_for_status = lambda: None
        with mock.patch("requests.post", return_value=ok) as post, mock.patch("requests.get", return_value=img):
            data = prov.generate("a cave", seed=3)
        self.assertEqual(data, b"IMG")
        self.assertIn("/models/black-forest-labs/flux-schnell/predictions", post.call_args.args[0])
        sent = post.call_args.kwargs["json"]["input"]
        self.assertEqual((sent["aspect_ratio"], sent["output_format"]), ("16:9", "png"))
        self.assertEqual((prov.images_done, prov.total_cost), (1, 0.003))  # list price from MODEL_PRESETS
        bad = mock.Mock(status_code=402, text="x")
        bad.json.return_value = {"detail": "Insufficient credit"}
        with mock.patch("requests.post", return_value=bad), self.assertRaisesRegex(ImageProviderError, "limit"):
            prov.generate("a")
        with override_settings(REPLICATE_API_TOKEN="t", RUNWARE_API_KEY="k"):
            chain = apply_model(RunwareImageProvider("k", "x"), "recraft-ai/recraft-v3")
            self.assertIsInstance(chain, FallbackImageProvider)
            self.assertEqual((chain.providers[0].name, chain.providers[0].model), ("replicate", "recraft-ai/recraft-v3"))
            self.assertEqual(apply_model(RunwareImageProvider("k", "x"), "ideogram:4.5@0").model, "ideogram:4.5@0")
        with override_settings(REPLICATE_API_TOKEN=""):
            plain = RunwareImageProvider("k", "x")
            self.assertIs(apply_model(plain, "recraft-ai/recraft-v3"), plain)  # no key: default provider kept


class SplitCloudflareTests(TestCase):
    def test_hero_scenes_use_the_reference_model_and_others_the_small_size(self):
        from django.test import override_settings

        from apps.videos.services.image_providers.cloudflare import (CloudflareImageProvider, SplitCloudflareProvider,
                                                                      parse_size)

        self.assertEqual((parse_size("1024x576"), parse_size("1000x500"), parse_size("")), ((1024, 576), None, None))
        klein = "@cf/black-forest-labs/flux-2-klein-4b"
        with override_settings(CLOUDFLARE_ACCOUNT_ID="a", CLOUDFLARE_API_TOKEN="t", CLOUDFLARE_IMAGE_MODEL=klein,
                               CLOUDFLARE_FACT_MODEL=klein, CLOUDFLARE_FACT_SIZE="1024x576"):
            prov = CloudflareImageProvider.from_settings()
        self.assertIsInstance(prov, SplitCloudflareProvider)
        self.assertTrue(prov.supports_reference)
        self.assertEqual((prov.hero.size, prov.other.size), ((1280, 720), (1024, 576)))
        with mock.patch.object(prov.hero, "generate", return_value=b"H") as h, mock.patch.object(prov.other, "generate", return_value=b"O") as o:
            self.assertEqual(prov.generate("p", seed=1, references=[b"ref"]), b"H")
            self.assertEqual(prov.generate("p", seed=1), b"O")
        h.assert_called_once()
        o.assert_called_once()
        data, _files = prov.other.build_multipart("p", 1, None)
        self.assertEqual((data["width"], data["height"]), ("1024", "576"))
