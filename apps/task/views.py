from django.contrib.auth.models import User
from django.core.mail import send_mail
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    DestroyAPIView,
    CreateAPIView,
    ListCreateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from apps.common.helpers import EmptySerializer
from apps.task.models import Task, Comment
from apps.task.serializers import (
    TaskSerializer,
    AssignTaskSerializer,
    CommentSerializer,
    CommentTaskSerializer,
)


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                name="status",
                description="Filter by Status",
                required=False,
                type=str,
                enum=[choice[0] for choice in Task.Status.choices],
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="user_id",
                description="Filter by User ID",
                required=False,
                type=int,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses=TaskSerializer(many=True),
        tags=["tasks"],
    ),
    post=extend_schema(tags=["tasks"]),
)
class TaskListCreateView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskSerializer

    def get_queryset(self):
        queryset = Task.objects.all()
        status = self.request.query_params.get("status")
        user_id = self.request.query_params.get("user_id")

        if status is not None:
            queryset = queryset.filter(status=status)
        if user_id is not None:
            queryset = queryset.filter(user__id=user_id)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task = Task.objects.create(
            title=serializer.validated_data["title"],
            description=serializer.validated_data.get("description"),
            status=Task.Status.OPEN,
            user=request.user,
            is_completed=False,
        )

        return Response({"id": task.id}, status=201)


class GetTaskView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    lookup_field = "id"


class DeleteTaskView(DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    lookup_field = "id"


class AssignTaskView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AssignTaskSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task_id = self.kwargs.get("id")
        user_id = serializer.validated_data["user_id"]

        task = get_object_or_404(Task, pk=task_id)
        user = get_object_or_404(User, pk=user_id)

        task.user = user
        task.save(update_fields=["user"])

        send_mail(
            subject="New Task",
            message=f"Task with id {task.id} is assigned to you",
            from_email="ttomson979@gmail.com",
            recipient_list=[user.email],
        )

        return Response(status=204)


class CompleteTaskView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EmptySerializer

    def create(self, request, *args, **kwargs):
        task_id = self.kwargs.get("id")
        task = get_object_or_404(Task, pk=task_id)
        task.status = Task.Status.COMPLETED.value
        task.save(update_fields=["status"])

        commenters = set()
        for c in task.comments.all():
            if c.user and c.user.email:
                commenters.add(c.user.email)

        for email in commenters:
            send_mail(
                subject="Task that you commented on is completed",
                message="The task you commented on has been marked as completed.",
                from_email="ttomson979@gmail.com",
                recipient_list=[email],
            )

        return Response(status=204)


class GetAllTaskCommentsView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentSerializer

    def get_queryset(self):
        task_id = self.kwargs.get("id")
        task = get_object_or_404(Task, pk=task_id)
        return task.comments.all()


class PostCommentTaskView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentTaskSerializer

    def create(self, request, *args, **kwargs):
        task_id = self.kwargs.get("id")
        task = get_object_or_404(Task, pk=task_id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = Comment.objects.create(
            text=serializer.validated_data["text"], task=task, user=request.user
        )

        if task.user and task.user.email:
            send_mail(
                subject="New Comment",
                message=comment.text,
                from_email="ttomson979@gmail.com",
                recipient_list=[task.user.email],
            )

        return Response({"id": comment.id, "text": comment.text}, status=201)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="query",
            required=False,
            type=str,
            location=OpenApiParameter.QUERY,
            description="Search by query",
        )
    ],
    responses=TaskSerializer(many=True),
    tags=["tasks"],
)
class TaskSearchView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskSerializer

    def get_queryset(self):
        search_term = self.request.query_params.get("query", "")
        return Task.objects.filter(title__icontains=search_term)
