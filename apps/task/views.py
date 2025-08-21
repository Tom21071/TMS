import uuid
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.mail import send_mail
from django.db.models import Sum
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveDestroyAPIView,
    get_object_or_404,
)
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.task.models import Attachment, Comment, Task, TimeLog
from apps.task.serializers import (
    AssignTaskSerializer,
    AttachmentSerializer,
    CommentSerializer,
    EmptySerializer,
    TaskSerializer,
    TimeLogSerializer,
)
from utils.minio_service import generate_presigned_url


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


class GetTaskView(RetrieveDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    lookup_field = "id"


class GetLastMonthTimeSumView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        now = timezone.now()
        first_day_last_month = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_day_last_month = now.replace(day=1) - timedelta(days=1)
        total_minutes = (
            TimeLog.objects.filter(
                date__gte=first_day_last_month, date__lte=last_day_last_month, user=request.user
            ).aggregate(total=Sum("duration"))["total"]
            or 0
        )
        return Response({"sum": total_minutes})


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
    serializer_class = CommentSerializer

    def create(self, request, *args, **kwargs):
        task_id = self.kwargs.get("id")
        task = get_object_or_404(Task, pk=task_id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = Comment.objects.create(text=serializer.validated_data["text"], task=task, user=request.user)

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


class StartTimerForTaskView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        task_id = self.kwargs.get("id")
        task = get_object_or_404(Task, pk=task_id)

        if TimeLog.objects.filter(task=task, user=request.user, duration__isnull=True).exists():
            return Response({"success": False, "error": "Timer already running"}, status=400)

        TimeLog.objects.create(task=task, user=request.user, date=timezone.now())
        return Response({"success": True}, status=200)


class EndTimerForTaskView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        task_id = self.kwargs.get("id")
        task = get_object_or_404(Task, pk=task_id)

        time_log = get_object_or_404(TimeLog, task=task, user=request.user, duration__isnull=True)

        now = timezone.now()
        time_log.duration = int((now - time_log.date).total_seconds() // 60)
        time_log.save()

        return Response(
            {
                "success": True,
                "duration_minutes": time_log.duration,
            },
            status=200,
        )


class GetAllTaskTimeLogsView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TimeLogSerializer

    def get_queryset(self):
        task_id = self.kwargs.get("id")
        task = get_object_or_404(Task, pk=task_id)
        return task.time_logs.all()


class PostTimeLogView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TimeLogSerializer

    def create(self, request, *args, **kwargs):
        task_id = self.kwargs.get("id")
        task = get_object_or_404(Task, pk=task_id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        TimeLog.objects.create(
            duration=serializer.validated_data["duration"],
            task=task,
            user=request.user,
            date=serializer.validated_data["date"],
        )
        return Response(status=201)


class GetTopTasksByTimeView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskSerializer

    def get(self, request, *args, **kwargs):
        amount = self.kwargs.get("amount")

        cache_key = f"top_tasks_{amount}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        qs = (
            Task.objects.annotate(total_duration=Sum("time_logs__duration"))
            .filter(total_duration__gt=0)
            .order_by("-total_duration")[:amount]
        )
        serializer = self.get_serializer(qs, many=True)
        data = serializer.data
        cache.set(cache_key, data, timeout=60)
        return Response(data)


class TaskAttachmentsView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, task_id):
        task = get_object_or_404(Task, pk=task_id)
        qs = task.attachments.order_by("-uploaded_at")
        return Response(AttachmentSerializer(qs, many=True).data)


class GenerateUploadURLView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id, file_name):
        task = get_object_or_404(Task, pk=task_id)

        object_key = f"{request.user.id}/{task.id}/{uuid.uuid4()}_{file_name}"
        url = generate_presigned_url("django-backend-dev-public", object_key)

        attachment = Attachment.objects.create(
            task=task,
            user=request.user,
            file_name=file_name,
            object_key=object_key,
        )

        return Response(
            {
                "upload_url": url,
                "file_id": attachment.id,
                "task_id": task.id,
            }
        )


class AttachmentConfirmView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, task_id):
        task = get_object_or_404(Task, pk=task_id)
        key = request.data["object_key"]
        attachment = task.attachments.create(file=key)
        return Response(AttachmentSerializer(attachment).data)
