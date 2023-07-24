from django.contrib import admin

from ..models import AmocrmPipeline


@admin.register(AmocrmPipeline)
class PipelinesAdmin(admin.ModelAdmin):
    list_display = ("name", "id", "sort", "is_archive", "is_main")
    list_filter = ("is_archive", "is_main")
    search_fields = ("id", "name",)
    ordering = ("sort", )
