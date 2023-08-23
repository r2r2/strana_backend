from common.loggers.models import BaseLogInline
from django import forms
from django.contrib import admin

from task_management.models import TaskInstance
from questionnaire.models import TaskInstanceLog


class TaskInstanceLogInline(BaseLogInline):
    model = TaskInstanceLog


@admin.register(TaskInstance)
class TaskInstanceAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
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

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if obj and obj.status.tasks_chain:
            task_chain = obj.status.tasks_chain
            fields_to_show = task_chain.task_fields.all()
            if not fields_to_show:
                return form
            excluded_fields = set(form.base_fields.keys()) - set(fields_to_show.values_list("field_name", flat=True))
            for field_name in excluded_fields:
                form.base_fields[field_name].widget = forms.HiddenInput()

        return form
