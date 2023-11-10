from django.contrib import admin

from ..models import DocumentInteraction


@admin.register(DocumentInteraction)
class InteractionDocumentAdmin(admin.ModelAdmin):
    list_display = ("name", "priority", "file", "icon")
    ordering = ["priority"]