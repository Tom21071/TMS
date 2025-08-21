from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.task.models import Task


@override_settings(ROOT_URLCONF="config.urls")
class TaskTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        token_res = self.client.post("/users/token", {"username": "testuser", "password": "testpass123"}, format="json")
        self.token = token_res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.task = Task.objects.create(title="Test Task", description="Test Desc", user=self.user)
        self.task_id = self.task.id

    def test_get_tasks_authenticated(self):
        res = self.client.get("/tasks")
        self.assertEqual(res.status_code, 200)

    def test_get_tasks_unauthenticated(self):
        self.client.credentials()
        res = self.client.get("/tasks")
        self.assertEqual(res.status_code, 401)

    def test_post_task(self):
        res = self.client.post("/tasks", {"title": "New Task", "description": "Details"}, format="json")
        self.assertEqual(res.status_code, 201)

    def test_get_task_by_id(self):
        res = self.client.get(f"/tasks/{self.task_id}")
        self.assertEqual(res.status_code, 200)

    def test_delete_task_by_id(self):
        res = self.client.delete(f"/tasks/{self.task_id}")
        self.assertEqual(res.status_code, 204)

    def test_assign_task(self):
        res = self.client.post(f"/tasks/{self.task_id}/assign", {"user_id": self.user.id}, format="json")
        self.assertEqual(res.status_code, 204)

    def test_comment_task(self):
        res = self.client.post(f"/tasks/{self.task_id}/comment", {"text": "This is a comment"}, format="json")
        self.assertEqual(res.status_code, 201)

    def test_get_all_comments_task(self):
        res = self.client.get(f"/tasks/{self.task_id}/comments")
        self.assertEqual(res.status_code, 200)

    def test_complete_task(self):
        res = self.client.post(f"/tasks/{self.task_id}/complete")
        self.assertIn(res.status_code, [204])

    def test_log_time_task(self):
        res = self.client.post(
            f"/tasks/{self.task_id}/log-time", {"date": "2025-08-18T10:00:00Z", "duration": "120"}, format="json"
        )
        self.assertEqual(res.status_code, 201)

    def test_get_task_timelogs(self):
        res = self.client.get(f"/tasks/{self.task_id}/timelogs")
        self.assertEqual(res.status_code, 200)

    def test_search_tasks(self):
        res = self.client.get("/tasks/search?query=Test")
        self.assertEqual(res.status_code, 200)

    def test_prev_month_time(self):
        res = self.client.get("/tasks/prev-month-time")
        self.assertEqual(res.status_code, 200)

    def test_top_tasks_by_logged_time(self):
        res = self.client.get("/tasks/top-by-logged-time/20")
        self.assertEqual(res.status_code, 200)

    def test_start_task(self):
        res = self.client.post(f"/timelog/{self.task.id}/start")
        self.assertEqual(res.status_code, 200)

    def test_finish_task(self):
        self.client.post(f"/timelog/{self.task.id}/start")
        res = self.client.post(f"/timelog/{self.task.id}/finish")
        self.assertEqual(res.status_code, 200)
