from django.contrib import admin

from ..models import AgreementStatus


@admin.register(AgreementStatus)
class AgreementStatusAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
