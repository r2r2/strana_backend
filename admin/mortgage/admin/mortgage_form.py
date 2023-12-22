from django.contrib import admin

from mortgage.models import MortgageForm


@admin.register(MortgageForm)
class MortgageFormAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "phone",
        "surname",
        "name",
        "patronymic",
    )
    search_fields = (
        "id",
        "phone",
        "surname",
        "name",
        "patronymic",
    )
