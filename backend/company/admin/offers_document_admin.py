from django.contrib.admin import register, ModelAdmin
from ..models import OffersDocument


@register(OffersDocument)
class OffersDocumentAdmin(ModelAdmin):
    list_filter = ("cities",)
    filter_horizontal = ("cities",)
