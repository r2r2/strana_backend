from django.contrib import admin

from ..models import TaskInstance


@admin.register(TaskInstance)
class TaskInstanceAdmin(admin.ModelAdmin):
    list_display = (
        "status",
        "comment",
        "task_amocrmid",
        "booking",
    )
    readonly_fields = ("updated_at", "created_at")
