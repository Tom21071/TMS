from django.conf import settings
from elasticsearch_dsl import Date, Document, Text, connections

connections.create_connection(alias="default", hosts=[getattr(settings, "ELASTICSEARCH_URL", "http://localhost:9200")])


class TaskDocument(Document):
    title = Text()
    description = Text()
    updated_at = Date()

    class Index:
        name = "tasks"


class CommentDocument(Document):
    text = Text()
    updated_at = Date()

    class Index:
        name = "comments"
