from django.contrib import admin

from ..models import AmocrmPipeline


@admin.register(AmocrmPipeline)
class PipelinesAdmin(admin.ModelAdmin):
    list_display = ("name", "id", "sort", "is_archive", "is_main")
    ordering = ("sort", )
