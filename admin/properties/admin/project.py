from django.contrib import admin

from ..models import Project


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
