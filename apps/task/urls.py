from django.urls import path

from apps.task.views import TasksView

urlpatterns = [
    path("tasks", TasksView.as_view(), name="tasks"),
]
