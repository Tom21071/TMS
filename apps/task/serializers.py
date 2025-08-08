from rest_framework import serializers

from apps.task.models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("id", "title", "description", "status", "is_completed", "user_id")
        read_only_fields = ("id", "status", "is_completed", "user_id")


class AssignTaskSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()


class CommentTaskSerializer(serializers.Serializer):
    text = serializers.CharField()


class CommentSerializer(serializers.Serializer):
    text = serializers.CharField()
