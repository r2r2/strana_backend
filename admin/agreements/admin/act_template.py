from django.contrib import admin

from ..models import ActTemplate


@admin.register(ActTemplate)
class ActTemplateAdmin(admin.ModelAdmin):
    list_display = ("template_name", "project")
