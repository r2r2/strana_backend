import os
from django.db import models
from django.urls import reverse


class StableDocument(models.Model):
    file_name = models.CharField(
        "Постоянное название документа",
        max_length=120
    )
    file = models.FileField(
        "Файл",
        upload_to="stable_document"
    )
    slug = models.SlugField(verbose_name="Слаг", max_length=100, unique=True)
    created = models.DateTimeField("Дата создания",  auto_now_add=True)
    updated = models.DateTimeField("Дата изменения",  auto_now=True)

    class Meta:
        verbose_name = "Файл со стабильной ссылкой"
        verbose_name_plural = "Файлы со стабильной ссылкой"

    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension

    def __str__(self):
        return f"{self.file_name}{self.extension()}"

    def get_absolute_url(self):
        return reverse("stable_file", kwargs={"slug": self.slug})
