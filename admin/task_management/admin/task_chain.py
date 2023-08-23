from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from task_management.models import TaskChain


@admin.register(TaskChain)
class TaskChainAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sensei_pid",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("updated_at", "created_at",)
    ordering = ("name",)
    search_fields = ("name", "id")
    filter_horizontal = ("booking_substage", "task_visibility", "task_fields")

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in ("booking_substage", "task_visibility", "task_fields"):
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field
