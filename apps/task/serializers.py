from rest_framework import serializers

from apps.task.models import Attachment, Task, TimeLog


class EmptySerializer:
    pass


class TaskSerializer(serializers.ModelSerializer):
    sum = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ("id", "title", "description", "status", "is_completed", "user_id", "sum")
        read_only_fields = ("id", "status", "is_completed", "user_id", "sum")

    def get_sum(self, obj):
        return sum(t.duration for t in obj.time_logs.all())


class AssignTaskSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()


class CommentSerializer(serializers.Serializer):
    text = serializers.CharField()


class TimeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        fields = ("id", "duration", "date", "user_id")
        read_only_fields = ("id", "user_id")


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ["id", "file_name", "uploaded_at"]
