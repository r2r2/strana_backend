from django.contrib import admin

from task_management.models import TaskInstanceLog


@admin.register(TaskInstanceLog)
class TaskInstanceLogAdmin(admin.ModelAdmin):
    list_display = ("__str__", "task_instance", "created")
    list_filter = ("use_case", "created")
    search_fields = ("content", "task_instance__id")
    readonly_fields = (
        "task_instance",
        "use_case",
        "content",
        "created",
        "state_before",
        "state_after",
        "state_difference",
        "error_data",
        "response_data",
    )
    list_per_page = 15
    save_on_top = True
    list_select_related = True
