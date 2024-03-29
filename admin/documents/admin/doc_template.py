from django.contrib import admin

from ..models import DocTemplate


@admin.register(DocTemplate)
class DocTemplateAdmin(admin.ModelAdmin):
    list_display = ("template_name", "project", "agreement_type", "type")
    search_fields = ("project__name", "template_name", "type", "agreement_type__name")
    list_filter = ("project", "type", "agreement_type__name")
