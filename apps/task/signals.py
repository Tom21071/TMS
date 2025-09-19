from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone

from .documents import CommentDocument, TaskDocument
from .models import Comment, Task


@receiver(post_save, sender=Task)
def index_task(sender, instance, **kwargs):
    TaskDocument(
        meta={"id": instance.id},
        title=instance.title,
        description=instance.description,
        updated_at=timezone.now(),
    ).save()


@receiver(post_delete, sender=Task)
def delete_task(sender, instance, **kwargs):
    TaskDocument.get(id=instance.id).delete()


@receiver(post_save, sender=Comment)
def index_comment(sender, instance, **kwargs):
    CommentDocument(
        meta={"id": instance.id},
        text=instance.text,
        updated_at=timezone.now(),
    ).save()


@receiver(post_delete, sender=Comment)
def delete_comment(sender, instance, **kwargs):
    CommentDocument.get(id=instance.id).delete()
