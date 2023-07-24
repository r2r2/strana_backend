from django.contrib import admin

from task_management.models import TaskStatus


@admin.register(TaskStatus)
class TaskStatusAdmin(admin.ModelAdmin):
    list_display = (
        "tasks_chain",
        "name",
        "description",
        "slug",
        "priority",
        "type",
    )
    readonly_fields = ("updated_at", "created_at")
    search_fields = ("tasks_chain__name", "name", "description", "slug")
    list_filter = ("type",)
