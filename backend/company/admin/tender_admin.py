from django.contrib.admin import register, ModelAdmin
from adminsortable2.admin import SortableAdminMixin
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter
from ..models import Tender


@register(Tender)
class TenderAdmin(SortableAdminMixin, ModelAdmin):
    list_display = ("title", "city", "category")
    list_filter = (
        ("category", RelatedDropdownFilter),
        ("city", RelatedDropdownFilter),
    )
