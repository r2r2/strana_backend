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
    is_active: bool = models.BooleanField(verbose_name="Активность", help_text="Активность", default=True)
    type = models.CharField(max_length=10, choices=[(type.value, type.name) for type in QuestionType])

    required: bool = models.BooleanField(
        verbose_name="Обязателен к ответу", help_text="Обязателен к ответу", default=True
    )

    question_group = models.ForeignKey(
        "questionnaire.QuestionGroup",
        on_delete=models.CASCADE,
        verbose_name="Группа вопроса",
        help_text="Группа вопроса",
        related_name="question_group",
        null=True, blank=True,
    )
    sort: int = models.IntegerField(default=0, verbose_name="Приоритет", help_text="Приоритет")


    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = "questionnaire_questions"
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
