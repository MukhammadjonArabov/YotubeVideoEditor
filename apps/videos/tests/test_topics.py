from django.test import TestCase

from apps.videos.models import Project
from apps.videos.services.topics import find_similar, find_similar_projects, normalize_topic, topic_hash


class TopicHashTests(TestCase):
    def test_hash_ignores_case_punctuation_order_and_stopwords(self):
        self.assertEqual(topic_hash("Why do cats purr?"), topic_hash("cats PURR — why"))
        self.assertEqual(topic_hash("The history of the fork"), topic_hash("history fork"))

    def test_plural_stemming(self):
        self.assertEqual(normalize_topic("Why cats purr"), normalize_topic("Why a cat purrs"))

    def test_different_topics_differ(self):
        self.assertNotEqual(topic_hash("Why do cats purr"), topic_hash("Why do dogs bark"))

    def test_find_similar_scores(self):
        cands = [(1, "Why do cats purr?"), (2, "The history of the fork"), (3, "why cats purr so loud")]
        found = find_similar("why do cats purr", cands)
        self.assertEqual(found[0].id, 1)
        self.assertEqual(found[0].score, 1.0)
        self.assertNotIn(2, [m.id for m in found])

    def test_project_saves_hash_and_detects_duplicates(self):
        p = Project.objects.create(topic="Why do cats purr?")
        self.assertEqual(p.topic_hash, topic_hash("cats purr"))
        self.assertEqual([m.id for m in find_similar_projects("why cats purr")], [p.id])
        self.assertEqual(find_similar_projects("why cats purr", exclude_id=p.id), [])
