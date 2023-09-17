from django.contrib import admin

from ..models import AdditionalServiceCondition


@admin.register(AdditionalServiceCondition)
class AdditionalServiceConditionAdmin(admin.ModelAdmin):
    search_fields = (
        "title",
    )
