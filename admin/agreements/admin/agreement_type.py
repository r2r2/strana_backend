from django.contrib import admin

from ..models import AgreementType


@admin.register(AgreementType)
class AgreementTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "priority", "created_at", "updated_at")
    ordering = ["priority"]
