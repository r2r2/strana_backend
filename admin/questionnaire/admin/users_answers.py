from django.contrib import admin

from ..models import UserAnswer


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ("__str__", "question_group", "question", "answer", "booking",)
    readonly_fields = ("user", "question_group", "question", "answer", "booking", "updated_at", "created_at",)
