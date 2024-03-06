from django.contrib import admin

from ..models import PrivilegeRequest


@admin.register(PrivilegeRequest)
class PrivilegeRequestAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "phone",
        "email",
    )
    readonly_fields = ("updated_at", "created_at",)
