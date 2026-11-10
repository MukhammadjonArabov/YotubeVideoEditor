from django.test import TestCase
from django.urls import reverse

from apps.videos.models import Project


class HomeViewTests(TestCase):
    def post(self, **extra):
        data = {"topic": "Why do cats purr?", "target_minutes": 2, "seconds_per_image": 8, "tts_provider": "edge"}
        data.update(extra)
        return self.client.post(reverse("videos:home"), data)

    def test_create_project(self):
        r = self.post()
        p = Project.objects.get()
        self.assertRedirects(r, reverse("videos:project_detail", args=[p.pk]))
        self.assertEqual(p.target_duration_sec, 120)

    def test_duplicate_requires_confirmation(self):
        self.post()
        r = self.post(topic="why cats PURR")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "xshash video")
        self.assertEqual(Project.objects.count(), 1)
        self.post(topic="why cats PURR", confirm_duplicate="on")
        self.assertEqual(Project.objects.count(), 2)

    def test_pages_render(self):
        self.post()
        p = Project.objects.get()
        for name, args in [("videos:project_list", []), ("videos:project_detail", [p.pk]),
                           ("videos:project_status", [p.pk]), ("videos:channels", []), ("videos:library", []), ("videos:policy", []),
                           ("videos:topic_check", [])]:
            self.assertEqual(self.client.get(reverse(name, args=args)).status_code, 200, name)
