from django.contrib import admin

from ..models import Section


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    search_fields = ("name", "building__name")
    list_display = ("name", "number", "building", "total_floors")
