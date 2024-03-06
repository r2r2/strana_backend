from common.loggers.models import BaseLogInline
from django.contrib import admin
from django.db import models

from ..utils import ReadableJSONFormField
from ..models import Agency, AgencyLog, AgencyGeneralType


class AgencyLogInline(BaseLogInline):
    model = AgencyLog


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)
    list_display = (
        "name",
        "is_approved",
        "is_deleted",
        "created_at",
        "inn",
        "amocrm_id",
        "city",
        "type",
        "general_type"
    )
    inlines = (AgencyLogInline, )
    search_fields = ("name", "inn", "amocrm_id", "type", "city")
    list_filter = ("created_at", "general_type", "city", "type")
    formfield_overrides = {
        models.JSONField: {'form_class': ReadableJSONFormField},
    }

    def save_model(self, request, obj, form, change):
        agency_slug = "agency"
        agency_tag = "АН"
        aggregator_tag = "Агрегатор"

        if not obj.general_type:
            default_type = AgencyGeneralType.objects.filter(slug=agency_slug).first()
            if default_type:
                obj.general_type = default_type

        if obj.general_type:
            if obj.general_type.slug == agency_slug:
                old_tag = aggregator_tag
                new_tag = agency_tag
            else:
                old_tag = agency_tag
                new_tag = aggregator_tag

            if obj.tags:
                result_tag = list({tag for tag in obj.tags if tag != old_tag})
                if new_tag not in result_tag:
                    result_tag.append(new_tag)
            else:
                result_tag = [new_tag]
            obj.tags = result_tag

        super().save_model(request, obj, form, change)
