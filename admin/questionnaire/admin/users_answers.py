from django.contrib import admin

from ..models import UserAnswer


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ("user_answer", "question_group", "question", "answer", "booking", "created_at")
    readonly_fields = ("user", "question_group", "question", "answer", "booking", "updated_at", "created_at",)
    search_fields = (
        "user__name",
        "user__surname",
        "user__patronymic",
        "user__phone",
        "question_group__title",
        "question__title",
        "answer__title",
        "booking__id",
        "booking__amocrm_id",
    )

    def user_answer(self, obj):
        return obj

    user_answer.short_description = 'Ответ пользователя'
    user_answer.admin_order_field = 'user'
