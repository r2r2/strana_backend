from django.contrib import admin

from task_management.models import Button


@admin.register(Button)
class ButtonAdmin(admin.ModelAdmin):
    list_display = (
        "label",
        "style",
        "slug",
        "status",
        "priority",
        "created_at",
        "updated_at",
    )
    autocomplete_fields = ("status",)
    readonly_fields = ("updated_at", "created_at")
    list_filter = ("created_at", "style")
    search_fields = ("status__name", "status__tasks_chain__name", "label", "slug")

