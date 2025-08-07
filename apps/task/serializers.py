from rest_framework import serializers

from apps.task.models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("id", "title", "description", "status", "is_completed")


class TaskGetAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("id", "title", "user_id")


class AssignTaskSerializer(serializers.Serializer):
    task_id = serializers.IntegerField()
    user_id = serializers.IntegerField()


class CompleteTaskSerializer(serializers.Serializer):
    task_id = serializers.IntegerField()


class CommentTaskSerializer(serializers.Serializer):
    task = serializers.IntegerField()  # ID of the task
    text = serializers.CharField()


class CommentSerializer(serializers.Serializer):
    text = serializers.CharField()
