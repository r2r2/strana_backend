from django.db import models

from questionnaire.entities import BaseQuestionnaireModel


class QuestionnaireField(BaseQuestionnaireModel):
    """
    12.11 Поля
    """
    slug: str = models.CharField(max_length=255, verbose_name='Слаг', null=True, blank=True)
    name: str = models.CharField(max_length=255, verbose_name='Название', null=True, blank=True)
    type: str = models.CharField(max_length=255, verbose_name='Тип', null=True, blank=True)
    description: str = models.TextField(verbose_name='Описание', null=True, blank=True)
    block = models.ForeignKey(
        "questionnaire.QuestionnaireDocumentBlock",
        on_delete=models.CASCADE,
        verbose_name='Блок',
        help_text='Блок',
        related_name="questionnaire_fields",
        null=True, blank=True
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        managed = False
        db_table = "questionnaire_fields"
        verbose_name = "Поле"
        verbose_name_plural = "10.12. [Опросник для пакета документов] Поля"
