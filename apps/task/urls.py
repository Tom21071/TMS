from django.urls import path

from apps.task.views import (
    AssignTaskView,
    CompleteTaskView,
    EndTimerForTaskView,
    GenerateUploadURLView,
    GetAllTaskCommentsView,
    GetAllTaskTimeLogsView,
    GetLastMonthTimeSumView,
    GetTaskView,
    GetTopTasksByTimeView,
    PostCommentTaskView,
    PostTimeLogView,
    StartTimerForTaskView,
    TaskAttachmentsView,
    TaskListCreateView,
    TaskSearchView,
)

urlpatterns = [
    path("tasks", TaskListCreateView.as_view(), name="tasks"),
    path("tasks/<int:id>", GetTaskView.as_view(), name="tasks-get-by-id"),
    path("tasks/<int:id>/assign", AssignTaskView.as_view(), name="tasks-assign"),
    path("tasks/<int:id>/complete", CompleteTaskView.as_view(), name="tasks-complete"),
    path("tasks/<int:id>/comment", PostCommentTaskView.as_view(), name="tasks-comment"),
    path(
        "tasks/<int:id>/comments",
        GetAllTaskCommentsView.as_view(),
        name="tasks-comments",
    ),
    path("tasks/search", TaskSearchView.as_view(), name="tasks-search"),
    path("timelog/<int:id>/start", StartTimerForTaskView.as_view(), name="task-start"),
    path("timelog/<int:id>/finish", EndTimerForTaskView.as_view(), name="task-finish"),
    path(
        "tasks/<int:id>/timelogs",
        GetAllTaskTimeLogsView.as_view(),
        name="task-time-logs",
    ),
    path("tasks/<int:id>/log-time", PostTimeLogView.as_view(), name="tasks-log-time"),
    path("tasks/prev-month-time", GetLastMonthTimeSumView.as_view(), name="time-last-month"),
    path(
        "tasks/top-by-logged-time/<int:amount>",
        GetTopTasksByTimeView.as_view(),
        name="time-top",
    ),
    path("tasks/<int:task_id>/attachments", TaskAttachmentsView.as_view(), name="task-attachments"),
    path(
        "tasks/<int:task_id>/presigned-url/<str:file_name>", GenerateUploadURLView.as_view(), name="task-presigned-url"
    ),
]
