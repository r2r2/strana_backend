from django.contrib import admin

from ..models import MortgageType


@admin.register(MortgageType)
class MortgageTypeAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "amocrm_id",
    )
