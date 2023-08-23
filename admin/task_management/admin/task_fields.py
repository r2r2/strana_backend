from django.contrib import admin

from task_management.models import TaskField


@admin.register(TaskField)
class TaskFieldAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "type",
    )
    ordering = ("name",)
    search_fields = ("name", "id")
