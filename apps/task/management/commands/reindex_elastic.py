from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch, helpers

from apps.task.documents import CommentDocument, TaskDocument
from apps.task.models import Comment, Task


class Command(BaseCommand):
    help = "Delete indices and reindex Task + Comment models into Elasticsearch"

    def handle(self, *args, **options):
        es = Elasticsearch("http://localhost:9200")

        # 1. Удаляем индексы
        for index in ("tasks", "comments"):
            if es.indices.exists(index=index):
                self.stdout.write(f"Deleting index: {index}")
                es.indices.delete(index=index)

        # 2. Создаём заново
        self.stdout.write("Recreating indices...")
        TaskDocument.init()
        CommentDocument.init()

        # 3. Индексация TASK
        self.stdout.write("Reindexing tasks...")
        task_actions = [
            {
                "_op_type": "index",
                "_index": "tasks",
                "_id": task.pk,
                **TaskDocument(
                    title=task.title,
                    description=task.description,
                ).to_dict(),
            }
            for task in Task.objects.iterator(chunk_size=500)
        ]
        if task_actions:
            helpers.bulk(es, task_actions)

        # 4. Индексация COMMENTS
        self.stdout.write("Reindexing comments...")
        comment_actions = [
            {
                "_op_type": "index",
                "_index": "comments",
                "_id": comment.pk,
                **CommentDocument(
                    text=comment.text,
                ).to_dict(),
            }
            for comment in Comment.objects.iterator(chunk_size=500)
        ]
        if comment_actions:
            helpers.bulk(es, comment_actions)

        self.stdout.write(self.style.SUCCESS("✅ Reindex completed!"))
