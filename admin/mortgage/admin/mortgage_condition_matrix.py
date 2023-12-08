from django.contrib import admin

from mortgage.models import MortgageConditionMatrix

@admin.register(MortgageConditionMatrix)
class MortgageConditionMatrixAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "is_there_agent",
        "default_value",
        "is_apply_for_mortgage",
        "created_at",
        "updated_at"
    )
    search_fields = (
        "id",
        "name",
    )
