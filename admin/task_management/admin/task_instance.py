from common.loggers.models import BaseLogInline
from django.contrib import admin

from ..models import TaskInstance
from questionnaire.models import TaskInstanceLog


class TaskInstanceLogInline(BaseLogInline):
    model = TaskInstanceLog


@admin.register(TaskInstance)
class TaskInstanceAdmin(admin.ModelAdmin):
    list_display = (
        "status",
        "booking",
        "task_amocrmid",
        "comment",
        "created_at",
        "updated_at",
    )
    autocomplete_fields = ("booking", "status")
    inlines = (TaskInstanceLogInline, )
    readonly_fields = ("updated_at", "created_at")
    list_filter = ("created_at",)
    search_fields = ("status__name", "status__tasks_chain__name", "booking__id", "booking__amocrm_id")

