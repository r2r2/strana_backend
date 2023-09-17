from django.contrib import admin

from ..models import AdditionalServiceConditionStep


@admin.register(AdditionalServiceConditionStep)
class AdditionalServiceConditionStepAdmin(admin.ModelAdmin):
    list_display = (
        "description",
        "condition",
        "active",
    )
