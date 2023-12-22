from django.contrib import admin

from mortgage.models import MortgageProgram


@admin.register(MortgageProgram)
class MortgageProgramAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "priority",
        "external_code",
        "slug",
    )
    search_fields = (
        "id",
        "name",
        "external_code",
        "slug",
    )
