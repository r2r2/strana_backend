from django.db import models

from ..entities import BaseQuestionnaireModel


class UserAnswer(BaseQuestionnaireModel):
    """
    Ответ пользователя
    """
    user = models.ForeignKey(
        "users.CabinetUser",
        models.SET_NULL,
        related_name='answered_user',
        verbose_name='Пользователь',
        help_text='Пользователь',
        blank=True, null=True,
    )
    question_group = models.ForeignKey(
        "questionnaire.QuestionGroup",
        on_delete=models.CASCADE,
        verbose_name="Группа вопроса",
        help_text="Группа вопроса",
        related_name="user_question_group",
        null=True, blank=True,
    )
    question = models.ForeignKey(
        "questionnaire.Question",
        on_delete=models.CASCADE,
        verbose_name="Вопрос",
        help_text="Вопрос",
        related_name="user_question",
        null=True, blank=True,
    )
    answer = models.ForeignKey(
        "questionnaire.Answer",
        on_delete=models.CASCADE,
        verbose_name="Ответ",
        help_text="Ответ",
        related_name="user_answer",
        null=True, blank=True,
    )
    booking = models.ForeignKey(
        "booking.Booking",
        on_delete=models.SET_NULL,
        verbose_name="Сделка",
        help_text="Сделка",
        related_name="user_booking",
        null=True, blank=True
    )

    def __str__(self):
        return f"Ответ пользователя {self.user}"

    class Meta:
        managed = False
        db_table = "questionnaire_users_answers"
        verbose_name = "Ответ пользователя"
        verbose_name_plural = "Ответы пользователей"
