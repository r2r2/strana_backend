from django.contrib import admin

from mortgage.models import MortgageBank


@admin.register(MortgageBank)
class MortgageBankAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "priority",
        "external_code",
        "uid",
    )
    search_fields = (
        "id",
        "name",
    )
