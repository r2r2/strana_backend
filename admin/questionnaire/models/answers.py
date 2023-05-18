from django.db import models

from ..entities import BaseQuestionnaireModel


class Answer(BaseQuestionnaireModel):
    """
    Ответ
    """
    title: str = models.CharField(
        max_length=150, verbose_name="Название", help_text="Название", null=True, blank=True
    )
    description: str = models.TextField(verbose_name="Тело ответа", help_text="Тело вопроса", null=True, blank=True)
    hint: str = models.TextField(verbose_name='Подсказка', help_text='Подсказка', null=True, blank=True)
    is_active: bool = models.BooleanField(verbose_name="Активность", help_text="Активность", default=True)
    is_default: bool = models.BooleanField(
        verbose_name="Ответ по умолчанию", help_text="Ответ по умолчанию", default=True
    )
    question = models.ForeignKey(
        "questionnaire.Question",
        on_delete=models.CASCADE,
        verbose_name="Вопросы",
        help_text="Вопросы",
        related_name="answers",
        null=True, blank=True,
    )
    sort: int = models.IntegerField(default=0, verbose_name="Приоритет", help_text="Приоритет")

    def __str__(self):
        return self.title if self.title else f"Ответ ID #{self.id}"

    class Meta:
        managed = False
        db_table = "questionnaire_answers"
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
