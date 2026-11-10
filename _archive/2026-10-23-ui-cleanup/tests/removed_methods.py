# --- from test_scenes.py
    def test_meta_and_settings_save(self):
        self.client.post(reverse("videos:project_meta_save", args=[self.p.pk]),
                         {"meta-title": "T", "meta-description": "D", "meta-tags_text": "a, b ,, c"})
        self.p.refresh_from_db()
        self.assertEqual(self.p.tags, ["a", "b", "c"])
        self.client.post(reverse("videos:project_settings_save", args=[self.p.pk]), {
            "set-topic": "Views topic", "set-target_minutes": "2.5", "set-seconds_per_image": "6",
            "set-tts_provider": "edge", "set-style_guide": ""})
        self.p.refresh_from_db()
        self.assertEqual(self.p.target_duration_sec, 150)
        self.assertEqual(self.p.seconds_per_image, 6)


# --- from test_scenes.py
    def test_add_move_delete_via_http(self):
        self.client.post(reverse("videos:scene_add", args=[self.p.pk]))
        self.assertEqual(self.p.scenes.count(), 2)
        r = self.client.post(reverse("videos:scene_move", args=[self.s.pk, "down"]))
        self.assertEqual(r.status_code, 200)
        self.s.refresh_from_db()
        self.assertEqual(self.s.order, 2)
        self.client.post(reverse("videos:scene_delete", args=[self.s.pk]))
        self.assertEqual(self.p.scenes.count(), 1)


# --- from test_scenes.py
    def test_inline_edit_with_upload(self):
        r = self.client.get(reverse("videos:scene_edit", args=[self.s.pk]))
        self.assertContains(r, "tahrirlash")
        buf = io.BytesIO()
        Image.new("RGB", (640, 480), "blue").save(buf, "PNG")
        buf.name = "x.png"
        buf.seek(0)
        r = self.client.post(reverse("videos:scene_edit", args=[self.s.pk]), {
            "narration": "Hello world", "image_prompt": "a caveman", "beat_type": "hook",
            "sfx0_tag": "whoosh", "sfx0_offset": "300", "sfx0_gain": "-10", "transition_in": "flash",
            "emotion": "scared", "intensity": "3", "pace": "slow", "pause_after_ms": "400", "camera_move": "shake",
            "music_cue": "drop_out", "on_screen_text": "  30,000   YEARS AGO ", "new_image": buf,
        })
        self.assertContains(r, "Hello world")
        self.s.refresh_from_db()
        self.assertEqual(self.s.sfx, [{"tag": "whoosh", "offset_ms": 300, "gain_db": -10.0}])
        self.assertEqual((self.s.emotion, self.s.intensity, self.s.pace, self.s.camera_move, self.s.music_cue),
                         ("scared", 3, "slow", "shake", "drop_out"))
        self.assertEqual(self.s.on_screen_text, "30,000 YEARS AGO")
        self.assertEqual(self.s.transition_in, "flash")
        self.assertContains(self.client.get(reverse("videos:scene_row", args=[self.s.pk])), "whoosh @300ms")
        self.assertTrue(self.s.image_locked)
        self.assertEqual(Image.open(self.s.image.path).size, (1920, 1080))
        self.s.image.delete()


# --- from test_scenes.py
    def test_studio_renders(self):
        r = self.client.get(reverse("videos:project_detail", args=[self.p.pk]))
        self.assertContains(r, "Sahnalar")
        self.assertContains(r, "Hello")


# --- from test_render.py
    def test_produce_view_passes_the_captions_choice_and_render_skips_spoken_subtitles(self):
        from apps.videos.models import Project

        p = Project.objects.create(topic="Captions", status=Project.Status.APPROVED)
        p.scenes.create(order=1, narration="Hello there, friend.")
        for value, expected in (("0", False), ("1", True)):
            with mock.patch("apps.videos.tasks.enqueue") as enq:
                self.client.post(f"/videolar/{p.pk}/yaratish/", {"quality": "preview", "captions": value})
            self.assertEqual(enq.call_args.args, ("produce_video", p, "preview", expected))
            Project.objects.filter(pk=p.pk).update(is_working=False)
        self.assertIn("Subtitrsiz", self.client.get(f"/videolar/{p.pk}/").content.decode())


# --- from test_manual_images.py
    def test_prompts_page_and_download(self):
        r = self.client.get(f"/videolar/{self.p.pk}/promptlar/")
        self.assertContains(r, "Hammasini nusxalash")
        self.assertContains(r, "one. Style: S")
        self.assertContains(self.client.get(f"/videolar/{self.p.pk}/promptlar/?ism=main_hero"), "main_hero")
        d = self.client.get(f"/videolar/{self.p.pk}/promptlar/?format=numbered")
        self.assertIn("attachment", d["Content-Disposition"])
        self.assertTrue(d.content.decode().startswith("001 | "))
        self.assertContains(self.client.get(f"/videolar/{self.p.pk}/"), "O'zim chizaman")


# --- from test_manual_images.py
    def test_bulk_upload_places_and_locks(self):
        files = [SimpleUploadedFile("002.png", png("blue"), "image/png"),
                 SimpleUploadedFile("001.png", png("red"), "image/png"),
                 SimpleUploadedFile("zzz.png", png(), "image/png")]
        r = self.client.post(f"/videolar/{self.p.pk}/rasm-yuklash/", {"images": files, "mode": "auto"}, follow=True)
        self.assertContains(r, "2 ta rasm sahnalarga joylandi")
        self.assertContains(r, "zzz.png")
        self.a.refresh_from_db(); self.b.refresh_from_db()
        self.assertTrue(self.a.image_locked and self.b.image_locked)
        self.assertEqual(Image.open(self.a.image.path).size, (1920, 1080))
        self.assertEqual(Image.open(self.a.image.path).getpixel((960, 540))[:3], (255, 0, 0))
        self.assertEqual(Image.open(self.b.image.path).getpixel((960, 540))[:3], (0, 0, 255))
        self.p.refresh_from_db()
        self.assertTrue(self.p.has_unrendered_changes)


# --- from test_director.py
    def test_batches_and_apply_via_button(self):
        from apps.videos import tasks

        with mock.patch.object(gemini_client, "generate_json", side_effect=self.fake) as gj, \
                mock.patch("apps.videos.tasks.async_task"):
            self.client.post(reverse("videos:project_direct", args=[self.p.pk]))
            tasks.direct_scenes(self.p.pk)
        self.assertEqual(gj.call_count, 2)  # 45 scenes -> batches of 40 + 5
        self.assertIn("41. [", "".join(c.args[0] for c in gj.call_args_list))
        self.p.refresh_from_db()
        self.assertFalse(self.p.is_working)
        self.assertIn("45", self.p.progress_message)
        self.assertEqual(self.p.scenes.get(order=1).emotion, "awe")
        self.assertEqual(self.p.scenes.get(order=1).camera_move, "pan_left")
        self.assertEqual(self.p.scenes.get(order=2).camera_move, "")  # same move twice in a row -> automatic
        self.assertTrue(self.p.has_unrendered_changes)
        page = self.client.get(reverse("videos:project_detail", args=[self.p.pk]))
        self.assertContains(page, "Rejissyor: qayta belgilash")
        self.assertContains(page, "His-tuyg")


# --- from test_script.py
    def test_bad_json(self):
        p = Project.objects.create(topic="T")
        r = self.client.post(reverse("videos:project_script_import", args=[p.pk]), {"script_text": "{nope"}, follow=True)
        self.assertContains(r, "JSON o")
        self.assertEqual(p.scenes.count(), 0)


# --- from test_script.py
    def test_import_json_file(self):
        import json

        from django.core.files.uploadedfile import SimpleUploadedFile
        p = Project.objects.create(topic="T", niche=Niche.active())
        payload = make_script(10).model_dump()
        f = SimpleUploadedFile("s.json", json.dumps(payload).encode(), content_type="application/json")
        with override_settings(GEMINI_API_KEY="", GEMINI_TEXT_MODEL=""):
            r = self.client.post(reverse("videos:project_script_import", args=[p.pk]), {"script_file": f}, follow=True)
        self.assertContains(r, "10 ta sahna")
        p.refresh_from_db()
        self.assertEqual(p.status, Project.Status.SCRIPT_READY)
        self.assertEqual(p.scenes.count(), 10)


# --- from test_script.py
    def test_approve_and_title_pick(self):
        p = Project.objects.create(topic="T", status=Project.Status.SCRIPT_READY,
                                   script_json={"title_alternatives": ["Alt one"], "mood": "calm"})
        p.scenes.create(order=1, narration="Hi")
        r = self.client.get(reverse("videos:project_detail", args=[p.pk]))
        self.assertContains(r, "Alt one")
        self.client.post(reverse("videos:project_use_title", args=[p.pk]), {"title": "Alt one"})
        self.client.post(reverse("videos:project_approve", args=[p.pk]))
        p.refresh_from_db()
        self.assertEqual(p.title, "Alt one")
        self.assertEqual(p.status, Project.Status.APPROVED)
        self.assertFalse(p.is_busy)  # approved alone is not "busy" (no endless polling)


# --- from test_script.py
    def test_cta_and_missing_key_message(self):
        p = Project.objects.create(topic="T", niche=Niche.active())
        with override_settings(GEMINI_API_KEY="", GEMINI_TEXT_MODEL=""):
            r = self.client.get(reverse("videos:project_detail", args=[p.pk]))
            self.assertContains(r, "GEMINI_API_KEY")
            r = self.client.post(reverse("videos:project_script_generate", args=[p.pk]), follow=True)
            self.assertContains(r, "GEMINI_API_KEY")
        with override_settings(GEMINI_API_KEY="k", GEMINI_TEXT_MODEL="m"):
            self.assertContains(self.client.get(reverse("videos:project_detail", args=[p.pk])), "Ssenariy yaratish")
            with mock.patch("apps.videos.tasks.async_task") as at:
                self.client.post(reverse("videos:project_script_generate", args=[p.pk]))
            self.assertEqual(at.call_args.args[0], "apps.videos.tasks.generate_script")


# --- line from test_script.py
        self.assertContains(self.client.get(reverse("videos:project_detail", args=[self.p.pk])), "📜 Fakt")


# --- from test_images.py
    def test_choose_model_validates_saves_and_is_applied(self):
        from apps.videos.services.image_providers import RunwareImageProvider, apply_model

        p = Project.objects.create(topic="Model choice")
        url = f"/videolar/{p.pk}/rasm-modeli/"
        self.client.post(url, {"model": "ideogram:4.5@0"})
        p.refresh_from_db()
        self.assertEqual(p.image_model, "ideogram:4.5@0")
        self.client.post(url, {"model": "", "custom": "not a model"})
        p.refresh_from_db()
        self.assertEqual(p.image_model, "ideogram:4.5@0")  # a bad id is refused, the old one stays
        self.client.post(url, {"model": "", "custom": "krea:krea@2-turbo"})
        p.refresh_from_db()
        self.assertEqual(p.image_model, "krea:krea@2-turbo")
        prov = apply_model(RunwareImageProvider("k", "runware:100@1"), p.image_model)
        self.assertEqual(prov.model, "krea:krea@2-turbo")
        self.assertEqual(apply_model(RunwareImageProvider("k", "x"), "").model, "x")  # empty = untouched
        self.assertContains(self.client.get(f"/videolar/{p.pk}/"), "Rasm modeli (Runware)")


# --- from test_images.py
    def test_generate_upload_and_delete_reference(self):
        from apps.videos.models import Niche

        n = Niche.active()
        n.character_description = "round white head"
        n.save()
        fp = FakeProvider()
        with mock.patch("apps.videos.services.image_providers.get_provider", return_value=fp):
            r = self.client.post("/nisha/personaj/")
        self.assertEqual(r.status_code, 302)
        n.refresh_from_db()
        self.assertTrue(n.character_reference)
        self.assertIn("round white head", fp.calls[0][0])
        page = self.client.get("/nisha/")
        self.assertContains(page, n.character_reference.url)
        self.client.post("/nisha/personaj/ochirish/")
        n.refresh_from_db()
        self.assertFalse(n.character_reference)


# --- from test_images.py
    def test_hero_redraw_button_queues_only_hero_scenes(self):
        ops.add_scene(self.p, narration="b", image_prompt="a map of Africa")
        with override_settings(**CF), mock.patch("apps.videos.tasks.async_task") as at:
            self.client.post(f"/videolar/{self.p.pk}/rasmlar/", {"mode": "hero"})
        args = at.call_args.args
        self.assertEqual(args[1:], (self.p.pk, [self.s.pk], True))


# --- line from test_images.py
        self.assertContains(self.client.get(f"/videolar/{p.pk}/"), "rasmlariga sarflangan")


# --- line from test_workflow.py
        page = self.client.get(reverse("videos:project_detail", args=[p.pk]))


# --- line from test_workflow.py
        self.assertContains(page, "Konsepsiya matni")


# --- line from test_workflow.py
        self.assertContains(page, "📚 manba")
