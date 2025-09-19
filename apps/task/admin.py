from django.contrib import admin

from apps.task.models import Task, TimeLog


class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "status", "user_id", "is_completed")
    list_filter = ("is_completed", "status", "user_id")
    search_fields = ("title", "description")


admin.site.register(TimeLog)
admin.site.register(Task, TaskAdmin)
