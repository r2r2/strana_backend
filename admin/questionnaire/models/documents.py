from django.db import models

from ..entities import BaseQuestionnaireModel


class QuestionnaireDocument(BaseQuestionnaireModel):
    """
    Документ сделки
    """
    label: str = models.CharField(
        max_length=150, verbose_name="Название", help_text="Название",blank=True, null=True
    )
    required: bool = models.BooleanField(verbose_name="Обязательный", help_text="Обязательный", default=True)
    doc_blocks = models.ForeignKey(
        "questionnaire.QuestionnaireDocumentBlock",
        on_delete=models.CASCADE,
        verbose_name="Блок документов",
        help_text="Блок документов",
        related_name="doc_blocks",
        null=True, blank=True
    )
    sort: int = models.IntegerField(default=0, verbose_name="Приоритет", help_text="Приоритет")

    def __str__(self):
        return self.label

    class Meta:
        managed = False
        db_table = "questionnaire_documents"
        verbose_name = "Документ сделки"
        verbose_name_plural = "Документы сделки"
