from django.contrib import admin

from ..models import Condition


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "question_groups",
        "questions",
        "answers",
        "created_at",
        "updated_at",
    )
    autocomplete_fields = (
        "questions",
        "answers",
    )
    readonly_fields = ("updated_at", "created_at",)
    search_fields = (
        "questions__title",
        "questions__question_group__title",
        "answers__title",
        "answers__question__title",
        "answers__question__question_group__title",
    )
