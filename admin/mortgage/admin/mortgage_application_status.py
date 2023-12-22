from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from mortgage.models import MortgageApplicationStatus


@admin.register(MortgageApplicationStatus)
class MortgageApplicationStatusAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "priority",
        "amocrm_statuses_list",
    )
    search_fields = (
        "id",
        "name",
    )

    def amocrm_statuses_list(self, obj):
        if obj.amocrm_statuses.exists():
            return [status.name for status in obj.amocrm_statuses.all()]
        else:
            return "-"

    amocrm_statuses_list.short_description = 'Выбранные статусы'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in ("amocrm_statuses",):
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field
