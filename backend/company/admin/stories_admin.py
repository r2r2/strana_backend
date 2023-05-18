from django.contrib import admin
from adminsortable2.admin import SortableInlineAdminMixin, SortableAdminMixin

from ..models import Story, StoryImage


class StoryImageInline(SortableInlineAdminMixin, admin.TabularInline):
    extra = 0
    model = StoryImage


@admin.register(Story)
class StoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = (StoryImageInline,)

    def get_queryset(self, request):
        return (
            super().get_queryset(request).prefetch_related("images").select_related("about_section")
        )
