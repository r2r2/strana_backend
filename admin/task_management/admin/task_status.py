from django.contrib import admin

from task_management.models import TaskStatus


@admin.register(TaskStatus)
class TaskStatusAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "slug",
        "priority",
        "type",
        "tasks_chain",
    )
    readonly_fields = ("updated_at", "created_at")
