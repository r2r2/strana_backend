from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from ..models import StranaOfficeAdmin


@admin.register(StranaOfficeAdmin)
class StranaOfficeAdminAdmin(admin.ModelAdmin):
    list_display = (
        "fio",
        "email",
        "projects_in_list",
    )

    def projects_in_list(self, obj):
        return [project.name for project in obj.projects.all()]

    projects_in_list.short_description = 'Проекты'
    projects_in_list.admin_order_field = 'project_name'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in ("projects", ):
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field
