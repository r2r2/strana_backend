from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django.contrib.admin import ModelAdmin, register, TabularInline

from ..admin_site import panel_site
from ..models import Progress, ProgressGallery, Camera, ProgressCategory


class ProgressGalleryInline(SortableInlineAdminMixin, TabularInline):
    model = ProgressGallery
    extra = 0


@register(Progress, site=panel_site)
class ProgressAdmin(SortableAdminMixin, ModelAdmin):
    inlines = (ProgressGalleryInline,)
    admin_label = "Ход строительства"


@register(Camera, site=panel_site)
class CameraAdmin(SortableAdminMixin, ModelAdmin):
    admin_label = "Ход строительства"


@register(ProgressCategory, site=panel_site)
class ProgressCategoryAdmin(ModelAdmin):
    raw_id_fields = ("progress",)
    list_filter = ("progress",)
    admin_label = "Ход строительства"
