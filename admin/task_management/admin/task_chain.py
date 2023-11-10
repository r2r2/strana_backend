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
    filter_horizontal = (
        "booking_substage",
        "task_visibility",
        "task_fields",
        "booking_source",
    )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in (
            "booking_substage",
            "task_visibility",
            "task_fields",
            "booking_source",
            "interchangeable_chains",
            "systems",
        ):
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."

        if db_field.name == "interchangeable_chains":
            msg = ("При создании задачи из текущей цепочки, задачи из выбранных цепочек удаляются. "
                   "Например, в сценариях бронирования, когда бесплатная бронь сменяется платной, "
                   "чтобы заменить задачи из других цепочек")
        elif db_field.name == "systems":
            msg = "Необходимо выбрать систему, где будут выводиться задания из текущей цепочки"
        elif db_field.name == "booking_source":
            msg = "Задачи из данной цепочки будут создаваться у данных типов сделок"
        elif db_field.name == "booking_substage":
            msg = "Первое задание в цепочке будет создано при достижении сделкой данного статуса"
        elif db_field.name == "task_visibility":
            msg = "Задание будет видно только в данных статусах, в последующих статусах оно будет не видно"

        form_field.help_text = msg
        return form_field
