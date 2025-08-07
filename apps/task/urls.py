from django.urls import path

from apps.task.views import (
    TasksView,
    AssignTaskView,
    CompleteTaskView,
    DeleteTaskView,
    CommentTaskView,
    TaskCommentsView,
    TaskSearchView,
)

urlpatterns = [
    path("tasks", TasksView.as_view(), name="tasks"),
    path("tasks/assign", AssignTaskView.as_view(), name="tasks"),
    path("tasks/complete", CompleteTaskView.as_view(), name="tasks"),
    path("tasks/<int:id>", DeleteTaskView.as_view(), name="delete-task"),
    path("tasks/comment", CommentTaskView.as_view(), name="tasks"),
    path("tasks/<int:id>/comments", TaskCommentsView.as_view(), name="task-comments"),
    path("tasks/search", TaskSearchView.as_view(), name="task-search"),
]
