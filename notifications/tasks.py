from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Sum
from django.template.loader import render_to_string
from django.utils.timezone import now

from apps.task.models import TimeLog


@shared_task
def send_email_async(subject, message, recipients, from_email=None, html_message=None):
    send_mail(subject, message, from_email or settings.DEFAULT_FROM_EMAIL, recipients, html_message=html_message)


@shared_task
def send_weekly_top20_reports():
    t = now()
    for u in get_user_model().objects.exclude(email__isnull=True).exclude(email=""):
        top = (
            TimeLog.objects.filter(user=u, date__gte=t - timedelta(days=7), date__lte=t)
            .values("task_id", "task__title")
            .annotate(total=Sum("duration"))
            .order_by("-total")[:20]
        )
        if top:
            ctx = {"user": u, "since": t - timedelta(days=7), "until": t, "items": list(top)}
            html = render_to_string("emails/weekly_top_tasks.html", ctx)
            send_email_async.delay("Your Weekly Top 20 Tasks by Time", "", [u.email], html_message=html)
