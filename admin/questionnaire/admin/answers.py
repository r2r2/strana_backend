from django.contrib import admin

from ..models import Answer


class AnswerAdminInline(admin.StackedInline):
    model = Answer
    extra = 0
    fields = (
        "title",
        "description",
        "hint",
        "is_active",
        "is_default",
        "question",
        "sort",
        ("updated_at", "created_at",)
    )
    readonly_fields = ("updated_at", "created_at",)