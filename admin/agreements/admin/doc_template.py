from django.contrib import admin

from ..models import DocTemplate


@admin.register(DocTemplate)
class DocTemplateAdmin(admin.ModelAdmin):
    list_display = ("template_name", "project", "agreement_type", "type")
