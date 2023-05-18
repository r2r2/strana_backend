from django.contrib.admin import register, ModelAdmin
from adminsortable2.admin import SortableAdminMixin
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter
from ..models import Vacancy


@register(Vacancy)
class VacancyAdmin(SortableAdminMixin, ModelAdmin):
    list_display = ("job_title", "cities", "category", "is_active")
    list_filter = (
        ("category", RelatedDropdownFilter),
        ("city", RelatedDropdownFilter),
    )
    actions = ['make_active', 'make_inactive']

    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    make_active.short_description = 'Сделать выбранные вакансии активными'

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)

    make_inactive.short_description = 'Сделать выбранные вакансии неактивными'

    def cities(self, instance):
        return '\n'.join([c.name for c in instance.city.all()])

    cities.short_description = "Города"
