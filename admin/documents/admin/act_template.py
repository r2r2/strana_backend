from django.contrib import admin

from ..models import ActTemplate


@admin.register(ActTemplate)
class ActTemplateAdmin(admin.ModelAdmin):
    list_display = ("template_name", "project")
    search_fields = ("project__name", "template_name")
    list_filter = ("project",)
