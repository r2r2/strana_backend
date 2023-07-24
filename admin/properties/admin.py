from django.contrib import admin
from .models import Property, Building, Project, Floor


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    search_fields = (
        "id",
        "article",
        "project__name",
        "area",
        "global_id",
        "type",
        "price",
        "final_price",
        "original_price",
        "area",
        "project__name",
        "building__name",
        "building__project__name",
        "floor__number",
        "floor__building__name",
        "floor__building__project__name",
        "number",
        "premise",
    )
    autocomplete_fields = (
        "building",
        "project",
        "floor",
    )
    list_display = (
        "global_id",
        "type",
        "final_price",
        "area",
        "project",
        "building",
        "floor",
        "status",
        "number",
    )


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    search_fields = ("name", "project__name")
    list_display = ("name", "project", "global_id")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    search_fields = (
        "name",
        "city__name",
        "global_id",
        "amocrm_enum",
        "amocrm_name",
        "amocrm_organization",
        "amo_responsible_user_id",
        "amo_pipeline_id",
        "slug",
    )
    list_filter = ("status",)
    list_display = (
        "global_id",
        "name",
        "status",
        "is_active",
        "priority",
        "city",
        "slug",
        "amocrm_enum",
        "amocrm_name",
        "amocrm_organization",
        "amo_responsible_user_id",
        "amo_pipeline_id",
    )
    autocomplete_fields = (
        "city",
    )


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    search_fields = (
        "number",
        "building__name",
        "building__project__name",
        "global_id",
    )
    autocomplete_fields = (
        "building",
    )
    list_display = ("global_id", "floor", "number")

    def floor(self, obj):
        return obj

    floor.short_description = 'Этажи'
    floor.admin_order_field = 'building__name'
