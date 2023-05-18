from django.contrib import admin

from .questions import QuestionAdminInline
from ..models import QuestionGroup


@admin.register(QuestionGroup)
class QuestionGroupAdmin(admin.ModelAdmin):
    list_display = ("title", "func_block",)
    inlines = (QuestionAdminInline,)
    readonly_fields = ("updated_at", "created_at",)
