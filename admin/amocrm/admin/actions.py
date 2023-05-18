from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from ..models import AmocrmAction


@admin.register(AmocrmAction)
class ActionsAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "role",)
    filter_horizontal = ("statuses",)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "statuses":
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field
