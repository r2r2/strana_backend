from django.contrib import admin

from ..models import Condition


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "question_groups",
        "questions",
        "answers",
    )
    readonly_fields = ("updated_at", "created_at",)
