from django.db import models

from ..entities import BaseQuestionnaireModel


class Condition(BaseQuestionnaireModel):
    """
    Условие для матрицы
    """
    title: str = models.CharField(
        max_length=150, verbose_name="Название", help_text="Название", null=True, blank=True
    )
    question_groups = models.ForeignKey(
        "questionnaire.QuestionGroup",
        on_delete=models.CASCADE,
        verbose_name="Группы вопросов",
        help_text="Группы вопросов",
        related_name="condition_question_group",
        null=True, blank=True,
    )
    questions = models.ForeignKey(
        "questionnaire.Question",
        on_delete=models.CASCADE,
        verbose_name="Вопросы",
        help_text="Вопросы",
        related_name="condition_question",
        null=True, blank=True,
    )
    answers = models.ForeignKey(
        "questionnaire.Answer",
        on_delete=models.CASCADE,
        verbose_name="Ответы",
        help_text="Ответы",
        related_name="condition_answer",
        null=True, blank=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = "questionnaire_conditions"
        verbose_name = "Условие для матрицы"
        verbose_name_plural = "Условия для матрицы"
