from django.contrib.admin import ModelAdmin, TabularInline, register
from adminsortable2.admin import SortableInlineAdminMixin, SortableAdminMixin
from common.admin import InlineFactory
from .models import (
    MainPage,
    MainPageSlide,
    MainPageIdeologyCard,
    MapText,
    MainPageStory,
    MainPageStoryImage,
)


class MainPageSlideAdmin(SortableInlineAdminMixin, TabularInline):
    model = MainPageSlide
    extra = 0


class MainPageIdeologyCardAdmin(SortableInlineAdminMixin, TabularInline):
    model = MainPageIdeologyCard
    extra = 0


@register(MainPage)
class MainPageAdmin(ModelAdmin):
    list_display = ("__str__", "site")
    list_filter = ("site",)
    inlines = (
        MainPageIdeologyCardAdmin,
        MainPageSlideAdmin,
    )


@register(MapText)
class MapTextAdmin(ModelAdmin):
    list_display = ("text", "red_text")


@register(MainPageStory)
class MainPageStoryAdmin(SortableAdminMixin, ModelAdmin):
    list_filter = ("page",)
    list_display = ("__str__", "page")
    inlines = InlineFactory(MainPageStoryImage)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("page")
