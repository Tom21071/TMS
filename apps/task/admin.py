from django.contrib import admin

from apps.task.models import Task


class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "is_completed")
    list_filter = ("is_completed",)
    search_fields = ("title", "description")


admin.site.register(Task, TaskAdmin)
