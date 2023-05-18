from django.contrib import admin

from ..models import AdditionalAgreementStatus


@admin.register(AdditionalAgreementStatus)
class AdditionalAgreementStatusAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
