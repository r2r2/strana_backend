from django.contrib import admin
from django.conf import settings
from django.utils.html import format_html

from .models import Feed, FeedManager
from feeds.constants import FeedType


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ("__str__", "is_active", "include_booked", "updated", "show_link")
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("buildings")

    def show_link(self, obj):
        domain = "https://localhost:8000" if settings.DEBUG else settings.DEFAULT_SITE_URL_REDIRECT
        links = []
        for kind, name in FeedType.choices:
            if kind in obj.template_type:
                link = f"{domain}/feed/{kind}/{obj.slug}/"
                links.append(f"<a href='{link}'target='_blank'>{link}</>")
        return format_html(str(links)[1:-1])

    show_link.short_description = "Ссылка"


@admin.register(FeedManager)
class FeedManagerAdmin(admin.ModelAdmin):
    list_display = ("__str__", "phone")
