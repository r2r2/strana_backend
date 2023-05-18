from django.db import models
from ckeditor.fields import RichTextField


class Document(models.Model):
    """
    Документ
    """

    text = RichTextField()
    slug = models.CharField(max_length=50)
    file = models.FileField(max_length=500, blank=True, null=True, upload_to="d/d/f")

    def __str__(self) -> str:
        return self.slug

    class Meta:
        managed = False
        db_table = "documents_document"
        verbose_name = "Документ"
        verbose_name_plural = "Документы"


class Escrow(models.Model):
    """
    Памятка Эскроу
    """

    slug = models.CharField(max_length=50)
    file = models.FileField(max_length=500, blank=True, null=True, upload_to="d/d/f")

    def __str__(self) -> str:
        return self.slug

    @property
    def file_url(self):
        return self.file.url

    class Meta:
        managed = False
        db_table = "documents_escrow"
        verbose_name = "Памятка Эскроу"
        verbose_name_plural = "Памятки Эскроу"
