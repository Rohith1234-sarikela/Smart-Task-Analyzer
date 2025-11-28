from datetime import date, timedelta
from django.test import TestCase
from . import scoring

class ScoringTests(TestCase):
    def test_overdue_task_has_higher_score_than_future_task(self):
        today = date.today()
        tasks = [
            {
                "id": 1,
                "title": "Overdue",
                "due_date": today - timedelta(days=2),
                "estimated_hours": 2,
                "importance": 5,
                "dependencies": [],
            },
            {
                "id": 2,
                "title": "Future",
                "due_date": today + timedelta(days=7),
                "estimated_hours": 2,
                "importance": 5,
                "dependencies": [],
            },
        ]

        scored = scoring.analyze_tasks(tasks, strategy="smart_balance")
        self.assertGreater(scored[0]["score"], scored[1]["score"])
        self.assertEqual(scored[0]["title"], "Overdue")

    def test_high_importance_beats_low_importance_with_same_other_fields(self):
        today = date.today()
        tasks = [
            {
                "id": 1,
                "title": "Low importance",
                "due_date": today + timedelta(days=1),
                "estimated_hours": 3,
                "importance": 3,
                "dependencies": [],
            },
            {
                "id": 2,
                "title": "High importance",
                "due_date": today + timedelta(days=1),
                "estimated_hours": 3,
                "importance": 9,
                "dependencies": [],
            },
        ]

        scored = scoring.analyze_tasks(tasks, strategy="high_impact")
        self.assertEqual(scored[0]["title"], "High importance")

    def test_circular_dependencies_are_detected(self):
        today = date.today()
        tasks = [
            {
                "id": 1,
                "title": "Task A",
                "due_date": today,
                "estimated_hours": 2,
                "importance": 5,
                "dependencies": [2],
            },
            {
                "id": 2,
                "title": "Task B",
                "due_date": today,
                "estimated_hours": 2,
                "importance": 5,
                "dependencies": [1],
            },
        ]

        scored = scoring.analyze_tasks(tasks, strategy="smart_balance")
        cyclic_flags = {t["title"]: t["has_circular_dependency"] for t in scored}
        self.assertTrue(cyclic_flags["Task A"])
        self.assertTrue(cyclic_flags["Task B"])
