from django.apps import AppConfig


class TaskConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.task"

    def ready(self):
        from .documents import CommentDocument, TaskDocument

        TaskDocument.init()
        CommentDocument.init()
