from django.contrib import admin

from ..models import FunctionalBlock


@admin.register(FunctionalBlock)
class FunctionalBlockAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", )
    readonly_fields = ("updated_at", "created_at",)
