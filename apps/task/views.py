from django.contrib.auth.models import User
from django.core.mail import send_mail
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.status import HTTP_204_NO_CONTENT

from apps.task.models import Task, Comment
from apps.task.serializers import (
    TaskSerializer,
    TaskGetAllSerializer,
    AssignTaskSerializer,
    CompleteTaskSerializer,
    CommentSerializer,
    CommentTaskSerializer,
)


class TasksView(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TaskGetAllSerializer
        return TaskSerializer

    def get(self, request: Request) -> Response:
        tasks = Task.objects.all()
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save(user=request.user)  # optional: add user FK
        return Response(self.get_serializer(task).data)


class AssignTaskView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AssignTaskSerializer  # used for input validation only

    def post(self, request: Request, *args, **kwargs) -> Response:
        # Validate input
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task_id = serializer.validated_data["task_id"]
        user_id = serializer.validated_data["user_id"]

        # Get objects
        task = get_object_or_404(Task, pk=task_id)
        user = get_object_or_404(User, pk=user_id)

        # Update and save
        task.user = user
        task.save(update_fields=["user"])

        send_mail(
            "smtp google",
            "Hello from Django",
            "ttomson979@gmail.com",
            ["alexandr.arciuk@ebs-integrator.com"],
        )

        # Use a proper serializer for output
        return Response()


class CompleteTaskView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CompleteTaskSerializer  # used for input validation only

    def post(self, request: Request, *args, **kwargs) -> Response:
        # Validate input
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task_id = serializer.validated_data["task_id"]

        # Get objects
        task = get_object_or_404(Task, pk=task_id)

        # Update and save
        task.status = Task.Status.COMPLETED.value
        task.save(update_fields=["status"])
        return Response()


class TaskCommentsView(ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        task_id = self.kwargs.get("id")
        task = get_object_or_404(Task, pk=task_id)
        return task.comments.all()


class CommentTaskView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentTaskSerializer

    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task_id = serializer.validated_data["task"]
        text = serializer.validated_data["text"]

        task = get_object_or_404(Task, pk=task_id)

        comment = Comment.objects.create(text=text, task=task, user=request.user)

        return Response({"id": comment.id}, status=201)


class DeleteTaskView(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request: Request, id: int, *args, **kwargs) -> Response:
        task = get_object_or_404(Task, pk=id)
        task.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class TaskSearchView(ListAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        search_term = self.request.query_params.get("search", "")
        return Task.objects.filter(title__icontains=search_term)


class TaskView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskGetAllSerializer  # FIXED

    def get(
        self, request: Request, task_id: int, user_id: int, *args, **kwargs
    ) -> Response:
        task = get_object_or_404(Task, pk=task_id)
        user = get_object_or_404(User, pk=user_id)

        task.user = user
        task.save(update_fields=["user"])

        return Response(self.get_serializer(task).data)
