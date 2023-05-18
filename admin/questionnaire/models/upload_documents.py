from uuid import uuid4

from django.db import models

from ..entities import BaseQuestionnaireModel


class QuestionnaireUploadDocument(BaseQuestionnaireModel):
    """
    Загруженный документ опросника
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    file_name: str = models.CharField(
        max_length=150, verbose_name="Название", help_text="Название", null=True, blank=True
    )
    url: str = models.CharField(
        max_length=2083,
        verbose_name="URL загруженного файла",
        help_text="URL загруженного файла",
        null=True, blank=True
    )
    uploaded_document = models.ForeignKey(
        "questionnaire.QuestionnaireDocument",
        on_delete=models.SET_NULL,
        verbose_name="Документ",
        help_text="Документ",
        related_name="uploaded_document",
        null=True, blank=True
    )
    booking = models.ForeignKey(
        "booking.Booking",
        on_delete=models.SET_NULL,
        verbose_name="Сделка",
        help_text="Сделка",
        related_name="booking",
        null=True, blank=True
    )

    def __str__(self):
        return self.file_name

    class Meta:
        managed = False
        db_table = "questionnaire_upload_documents"
        verbose_name = "Загруженный документ"
        verbose_name_plural = "Загруженные документы"
