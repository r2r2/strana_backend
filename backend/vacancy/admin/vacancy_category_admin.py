from django.contrib.admin import register, ModelAdmin
from adminsortable2.admin import SortableAdminMixin
from ..models import VacancyCategory


@register(VacancyCategory)
class VacancyCategoryAdmin(SortableAdminMixin, ModelAdmin):
    pass
