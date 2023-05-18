from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django.contrib.admin import ModelAdmin, register, TabularInline
from django.utils.html import format_html
from .models import City, MetroLine, Metro, Transport, Map, ProjectSlide
from .tasks import calculate_city_fields_task


class ProjectSlideAdmin(SortableInlineAdminMixin, TabularInline):
    model = ProjectSlide
    extra = 0


@register(City)
class CityAdmin(SortableAdminMixin, ModelAdmin):
    list_display = ("__str__", "active")
    list_filter = ("active",)
    actions = ("calculate_fields",)
    inlines = (ProjectSlideAdmin,)

    def calculate_fields(self, request, queryset):
        calculate_city_fields_task()

    calculate_fields.short_description = "Просчитать поля"


@register(Metro)
class MetroAdmin(ModelAdmin):
    list_display = ("name", "line")
    list_filter = ("line",)
    search_fields = ("name", "line__name")


class MetroInline(TabularInline):
    model = Metro
    extra = 0
    ordering = ("order",)


@register(MetroLine)
class MetroLineAdmin(ModelAdmin):
    list_display = ("name", "get_color")
    inlines = (MetroInline,)

    def get_color(self, obj):
        return format_html(
            f'<div style="width: 60px; height: 20px; ' f'background: {obj.color}"></div>'
        )

    get_color.short_description = "Цвет"


@register(Transport)
class TransportAdmin(ModelAdmin):
    pass


@register(Map)
class MapAdmin(ModelAdmin):
    save_as = True
