from django.contrib.admin import register, ModelAdmin
from adminsortable2.admin import SortableAdminMixin
from ..models import DocumentCategory


@register(DocumentCategory)
class DocumentCategoryAdmin(SortableAdminMixin, ModelAdmin):
    pass
