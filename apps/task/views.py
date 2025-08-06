from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED

from apps.task.models import Task
from apps.task.serializers import TaskSerializer


class TasksView(GenericAPIView):
    serializer_class = TaskSerializer
    permission_classes = (AllowAny,)

    def get(self, request: Request) -> Response:
        tasks = Task.objects.all()
        return Response(self.get_serializer(tasks, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        blog = Task.objects.create(**validated_data)
        return Response(self.get_serializer(blog).data, status=HTTP_201_CREATED)
