from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from ..models import Matrix


@admin.register(Matrix)
class MatrixAdmin(admin.ModelAdmin):
    filter_horizontal = ("conditions",)
    readonly_fields = ("updated_at", "created_at",)
    list_display = ("__str__", "get_conditions_info_on_list", "created_at", "updated_at")
    search_fields = (
        "conditions__title",
        "conditions__question_groups__title",
        "conditions__questions__title",
        "conditions__answers__title",
    )

    def get_queryset(self, request):
        qs = self.model._default_manager.get_queryset().distinct()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def get_conditions_info_on_list(self, obj):
        if obj.conditions.exists():
            return [condition for condition in obj.conditions.all()]
        else:
            return "-"

    get_conditions_info_on_list.short_description = 'Условия для матрицы'
    get_conditions_info_on_list.admin_order_field = 'conditions'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "conditions":
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field
