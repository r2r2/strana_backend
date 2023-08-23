from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from task_management.models import Button


@admin.register(Button)
class ButtonAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = (
        "label",
        "style",
        "slug",
        "get_statuses_display",
        "priority",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("updated_at", "created_at")
    list_filter = ("created_at", "style")
    search_fields = ("label", "slug")

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

    def get_statuses_display(self, obj):
        return ", ".join(str(status) for status in obj.statuses.all())

    get_statuses_display.short_description = "Статусы"
