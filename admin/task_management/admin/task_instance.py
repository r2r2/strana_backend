from common.loggers.models import BaseLogInline
from django.contrib import admin

from ..models import TaskInstance, TaskInstanceLog


class TaskInstanceLogInline(BaseLogInline):
    model = TaskInstanceLog


@admin.register(TaskInstance)
class TaskInstanceAdmin(admin.ModelAdmin):
    list_display = (
        "status",
        "comment",
        "task_amocrmid",
        "booking",
    )
    inlines = (TaskInstanceLogInline, )
    readonly_fields = ("updated_at", "created_at")
