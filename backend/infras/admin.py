from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from panel_manager.tasks import update_infra_objects
from .models import (
    Infra,
    InfraCategory,
    InfraType,
    MainInfra,
    SubInfra,
    RoundInfra,
    InfraContent,
    MainInfraContent,
)


class InfraContentInline(admin.TabularInline):
    model = InfraContent
    extra = 0


class MainInfraContentInline(admin.TabularInline):
    model = MainInfraContent
    extra = 0


@admin.register(Infra)
class InfraAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "show_in_site", "show_in_panel")
    list_filter = ("project", "show_in_site", "show_in_panel")
    inlines = (InfraContentInline,)
    actions = ["update_from_yandex"]

    def update_from_yandex(self, request, queryset):
        update_infra_objects()

    update_from_yandex.short_description = "Поиск инфраструктуры в яндексе"


@admin.register(InfraType)
class InfraTypeAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


@admin.register(InfraCategory)
class InfraCategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


@admin.register(MainInfra)
class MainInfraAdmin(admin.ModelAdmin):
    list_display = ("name", "project")
    list_filter = ("project",)
    inlines = (MainInfraContentInline,)


@admin.register(SubInfra)
class SubInfraAdmin(admin.ModelAdmin):
    list_display = ("name", "project")
    list_filter = ("project",)


@admin.register(RoundInfra)
class RoundInfraAdmin(admin.ModelAdmin):
    list_display = ("name", "project")
    list_filter = ("project",)
