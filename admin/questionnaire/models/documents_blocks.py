from django.db import models

from ..entities import BaseQuestionnaireModel


class QuestionnaireDocumentBlock(BaseQuestionnaireModel):
    """
    Блок документов опросника
    """
    title: str = models.CharField(
        max_length=150, verbose_name="Название", help_text="Название", null=True, blank=True
    )
    label: str = models.TextField(verbose_name='Подсказка', help_text='Подсказка', null=True, blank=True)
    description: str = models.TextField(
        verbose_name="Описание подсказки", help_text="Описание подсказки", null=True, blank=True
    )
    matrix = models.ForeignKey(
        "questionnaire.Matrix",
        on_delete=models.CASCADE,
        verbose_name="Матрица",
        help_text="Матрица",
        related_name="doc_blocks_matrix",
        null=True, blank=True
    )
    sort: int = models.IntegerField(default=0, verbose_name="Приоритет", help_text="Приоритет")
    required: bool = models.BooleanField(
        verbose_name="Не зависит от условий", help_text="Не зависит от условий", default=False
    )

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = "questionnaire_documents_blocks"
        verbose_name = "Блок документов"
        verbose_name_plural = "Блоки документов"
