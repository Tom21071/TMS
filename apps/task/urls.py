from django.urls import path

from apps.task.views import (
    AssignTaskView,
    CompleteTaskView,
    DeleteTaskView,
    PostCommentTaskView,
    GetAllTaskCommentsView,
    TaskSearchView,
    GetTaskView,
    TaskListCreateView,
)

urlpatterns = [
    path("tasks", TaskListCreateView.as_view(), name="tasks"),
    path("tasks/<int:id>", GetTaskView.as_view(), name="tasks-get-by-id"),
    path("tasks/<int:id>/assign", AssignTaskView.as_view(), name="tasks-assign"),
    path("tasks/<int:id>/complete", CompleteTaskView.as_view(), name="tasks-complete"),
    path("tasks/<int:id>", DeleteTaskView.as_view(), name="delete-task"),
    path("tasks/<int:id>/comment", PostCommentTaskView.as_view(), name="tasks-comment"),
    path(
        "tasks/<int:id>/comments",
        GetAllTaskCommentsView.as_view(),
        name="tasks-comments",
    ),
    path("tasks/search", TaskSearchView.as_view(), name="tasks-search"),
]
