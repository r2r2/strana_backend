from django.db import models

from ..entities import BaseQuestionnaireModel


class QuestionGroup(BaseQuestionnaireModel):
    """
    Группа вопросов
    """
    title: str = models.CharField(
        max_length=150, verbose_name="Название", help_text="Название", null=True, blank=True
    )
    func_block = models.ForeignKey(
        "questionnaire.FunctionalBlock",
        on_delete=models.CASCADE,
        verbose_name="Функциональный блок",
        help_text="Функциональный блок",
        related_name="func_block",
        null=True, blank=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = "questionnaire_question_groups"
        verbose_name = "Группа вопроса"
        verbose_name_plural = "Группы вопросов"
