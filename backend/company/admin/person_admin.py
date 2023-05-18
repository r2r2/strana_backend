from django.contrib.admin import register, ModelAdmin
from adminsortable2.admin import SortableAdminMixin
from ..models import Person


@register(Person)
class PersonAdmin(SortableAdminMixin, ModelAdmin):
    list_display = ("__str__", "category")
    list_filter = ("category",)
