from django.db import models

from ..entities import BaseQuestionnaireModel


class QuestionnaireDocument(BaseQuestionnaireModel):
    """
    Документ сделки
    """
    label: str = models.CharField(
        max_length=150,
        verbose_name="Название",
        blank=True,
        null=True,
        help_text="Определяет список документов, которые будут загружаться по сделке",
    )
    required: bool = models.BooleanField(
        verbose_name="Обязательный", default=True, help_text="Документ обязателен для заполнения"
    )
    doc_blocks = models.ForeignKey(
        "questionnaire.QuestionnaireDocumentBlock",
        on_delete=models.CASCADE,
        verbose_name="Блок документов",
        related_name="doc_blocks",
        null=True,
        blank=True,
        help_text="Документ будет заполняться в данном блоке",
    )
    sort: int = models.IntegerField(default=0, verbose_name="Приоритет", help_text="Приоритет")

    def __str__(self):
        doc_blocks_title = self.doc_blocks.title if self.doc_blocks else "-"
        return f"[{doc_blocks_title}] {self.label}"

    class Meta:
        managed = False
        db_table = "questionnaire_documents"
        verbose_name = "Документ сделки"
        verbose_name_plural = " 10.7. [Опросник для пакета документов] Документы сделки"
