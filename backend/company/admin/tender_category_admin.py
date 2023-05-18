from django.contrib.admin import register, ModelAdmin
from adminsortable2.admin import SortableAdminMixin
from ..models import TenderCategory


@register(TenderCategory)
class TenderCategoryAdmin(SortableAdminMixin, ModelAdmin):
    pass
