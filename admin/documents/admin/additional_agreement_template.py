from django.contrib import admin

from ..models import AdditionalAgreementTemplate


@admin.register(AdditionalAgreementTemplate)
class AdditionalAgreementTemplateAdmin(admin.ModelAdmin):
    list_filter = ("type", "project")
    list_display = ("template_name", "project", "type")
    search_fields = ("project__name", "template_name", "type")
