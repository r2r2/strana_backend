from datetime import datetime
from django.db import models
from ckeditor.fields import RichTextField


class DocumentArchive(models.Model):
    """
    23.5 Архив документов (шаблонов оферт)
    """

    offer_text = RichTextField()
    slug = models.CharField(verbose_name="Слаг", max_length=50)
    file = models.FileField(
        verbose_name="Файл",
        max_length=500,
        blank=True,
        null=True,
        upload_to="d/d/d_arch"
    )
    date_time: datetime = models.DateTimeField(
        verbose_name="Дата, время создания",
        auto_now_add=True
    )

    def __str__(self) -> str:
        return f"{self.slug}"

    class Meta:
        verbose_name = "Архив оферт"
        verbose_name_plural = "23.5 Архив шаблонов оферт"
        db_table = "documents_document_archive"

