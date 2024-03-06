from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from privilege_program.models import PrivilegeCategory


@admin.register(PrivilegeCategory)
class PrivilegeCategoryAdmin(admin.ModelAdmin):
    readonly_fields = ("updated_at", "created_at",)
    ordering = ("filter_priority",)
    filter_horizontal = ("cities",)
    prepopulated_fields = {'slug': ('title',)}
    list_display = (
        "title",
        "slug",
        "is_active",
        "dashboard_priority",
        "filter_priority",
        "get_cities_on_list",
        "display_type",
    )

    def get_cities_on_list(self, obj):
        if obj.cities.exists():
            return [city.name for city in obj.cities.all()]
        else:
            return "-"

    get_cities_on_list.short_description = 'Города'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "cities":
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field
