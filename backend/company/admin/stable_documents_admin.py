from django.contrib import admin
from django.conf import settings
from django.utils.html import format_html

from ..models import StableDocument

@admin.register(StableDocument)
class StableDocumentAdmin(admin.ModelAdmin):
    list_display = ("file_name", "show_link")

    def show_link(self, obj):
        domain = "http://localhost:8000" if settings.DEBUG else settings.DEFAULT_SITE_URL_REDIRECT
        link = f"{domain}{obj.get_absolute_url()}"
        return format_html(f"<a href='{link}'target='_blank'>{link}</>")

    show_link.short_description = "Ссылка"

