import random
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.task.models import Task, TimeLog, User


class Command(BaseCommand):
    help = "Generates 25,000 tasks and 50,000 time logs with random data."

    def handle(self, *args, **options):
        users = list(User.objects.all())
        if not users:
            raise CommandError("No users found in the database.")

        statuses = [choice[0] for choice in Task.Status.choices]

        self.stdout.write("Generating 25,000 tasks...")

        tasks = []
        for i in range(25000):
            task = Task(
                title=f"Task {i + 1}",
                description=f"This is the description for Task {i + 1}",
                status=random.choice(statuses),
                user=random.choice(users),
                is_completed=random.choice([True, False]),
            )
            tasks.append(task)

        Task.objects.bulk_create(tasks, batch_size=1000)
        self.stdout.write(self.style.SUCCESS("25,000 tasks created."))

        # Refresh tasks from DB to get their IDs
        all_tasks = list(Task.objects.all())

        self.stdout.write("Generating 50,000 time logs...")

        time_logs = []
        now = timezone.now()

        for _ in range(50000):
            time_log = TimeLog(
                task=random.choice(all_tasks),
                user=random.choice(users),
                duration=random.randint(1, 100),
                date=now - timedelta(days=random.randint(0, 100)),  # Random past year
            )
            time_logs.append(time_log)

        TimeLog.objects.bulk_create(time_logs, batch_size=1000)
        self.stdout.write(self.style.SUCCESS("50,000 time logs created."))
