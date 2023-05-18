from django.contrib import admin

from .answers import AnswerAdminInline
from ..models import Question


class QuestionAdminInline(admin.StackedInline):
    model = Question
    extra = 0
    fields = (
        "title", "description", "is_active", "type", "required", "question_group",
        ("updated_at", "created_at",)
    )
    readonly_fields = ("updated_at", "created_at",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "question_group", "sort", )
    inlines = (AnswerAdminInline,)
    readonly_fields = ("updated_at", "created_at",)
