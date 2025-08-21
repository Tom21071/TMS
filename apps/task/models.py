from django.contrib.auth import get_user_model
from django.db import models

from utils.minio_service import get_minio_client

User = get_user_model()


class Task(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELED = "CANCELED", "Canceled"
        ARCHIVED = "ARCHIVED", "Archived"

    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    is_completed = models.BooleanField(default=False)


class Comment(models.Model):
    text = models.TextField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")


class TimeLog(models.Model):
    date = models.DateTimeField()
    duration = models.IntegerField(null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="time_logs")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="time_logs")


class Attachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="attachments", null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attachments", null=True)

    file_name = models.CharField(max_length=255, null=True, blank=True)  # original filename
    object_key = models.CharField(max_length=500, null=True, blank=True)  # path in MinIO

    uploaded_at = models.DateTimeField(auto_now_add=True)

    @property
    def file_url(self):
        s3 = get_minio_client()
        return s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": "django-backend-dev-public", "Key": self.object_key},
            ExpiresIn=3600,
        )
