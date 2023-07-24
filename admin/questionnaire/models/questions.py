from enum import Enum

from django.db import models

from ..entities import BaseQuestionnaireModel


class Question(BaseQuestionnaireModel):
    """
    Вопрос
    """
    class QuestionType(str, Enum):
        """
        Тип вопроса
        """
        SINGLE: str = "single"
        MULTIPLE: str = "multiple"

    title: str = models.CharField(
        max_length=150, verbose_name="Название", help_text="Название", null=True, blank=True
    )
    description: str = models.TextField(
        verbose_name="Тело вопроса", help_text="Тело вопроса", null=True, blank=True
    )
    is_active: bool = models.BooleanField(
        verbose_name="Активность", default=True, help_text="Неактивные вопросы не выводятся в списке"
    )
    type = models.CharField(
        verbose_name="Тип",
        max_length=10,
        choices=[(type.value, type.name) for type in QuestionType],
        help_text="Тип вопроса",
    )

    required: bool = models.BooleanField(
        verbose_name="Обязателен к ответу", help_text="Обязателен к ответу", default=True
    )

    question_group = models.ForeignKey(
        "questionnaire.QuestionGroup",
        on_delete=models.CASCADE,
        verbose_name="Группа вопроса",
        related_name="question_group",
        null=True,
        blank=True,
        help_text="Определяет, в каком опроснике будет использоваться данные вопрос",
    )
    sort: int = models.IntegerField(
        default=0,
        verbose_name="Приоритет",
        help_text="Чем меньше приоритет. тем раньше будет выводиться вопрос в списке",
    )

    def __str__(self):
        question_group_title = self.question_group.title if self.question_group else "-"
        return f"[{question_group_title}] {self.title}"

    class Meta:
        managed = False
        db_table = "questionnaire_questions"
        verbose_name = "Вопрос"
        verbose_name_plural = " 10.1. Вопросы"
