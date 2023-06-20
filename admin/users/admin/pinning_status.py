from django.contrib.admin import register, ModelAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple

from users.models.pinning_status import PinningStatus


@register(PinningStatus)
class PinningStatusAdmin(ModelAdmin):
    list_display = ("id", "_cities", "priority", "result")
    filter_horizontal = ("cities", "pipelines", "statuses")
    save_as = True

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in ["cities", "pipelines", "statuses"]:
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field
