from django.contrib import admin

from ..models import StranaOfficeAdmin


@admin.register(StranaOfficeAdmin)
class StranaOfficeAdminAdmin(admin.ModelAdmin):
    list_display = (
        "fio",
        "email",
        "project"
    )
