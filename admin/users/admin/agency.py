from common.loggers.models import BaseLogInline
from django.contrib import admin
from django.db import models

from ..utils import ReadableJSONFormField
from ..models import Agency, AgencyLog


class AgencyLogInline(BaseLogInline):
    model = AgencyLog


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
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
    )
    inlines = (AgencyLogInline, )
    search_fields = ("name", "inn", "amocrm_id", "type", "city__name")
    list_filter = ("created_at",)
    formfield_overrides = {
        models.JSONField: {'form_class': ReadableJSONFormField},
    }
