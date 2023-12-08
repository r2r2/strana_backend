from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from task_management.models.task_group_status import TaskGroupStatus


@admin.register(TaskGroupStatus)
class TaskGroupStatusAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "priority",
        "task_chain",
        "get_statuses_on_list",
    )
    readonly_fields = ("updated_at", "created_at",)
    ordering = ("name",)
    search_fields = ("name", "id")
    list_filter = ("name", "id")
    filter_horizontal = (
        "statuses",
    )

    def get_statuses_on_list(self, obj):
        if obj.statuses.exists():
            return [status.name for status in obj.statuses.all()]
        else:
            return "-"

    get_statuses_on_list.short_description = 'Статусы задач'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in ("statuses",):
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field
