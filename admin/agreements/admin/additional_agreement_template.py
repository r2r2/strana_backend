from django.contrib import admin

from ..models import AdditionalAgreementTemplate


@admin.register(AdditionalAgreementTemplate)
class AdditionalAgreementTemplateAdmin(admin.ModelAdmin):
    list_filter = ("type",)
    list_display = ("template_name", "project", "type")
