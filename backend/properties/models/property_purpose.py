from django.db import models
from ckeditor.fields import RichTextField
from django.core.files.storage import default_storage


class PropertyPurpose(models.Model):
    """ Модель назначения объекта собственности """

    name = models.CharField(verbose_name="Название", max_length=64)
    icon = models.FileField(verbose_name="Иконка", blank=True, upload_to="p/pp")
    icon_content = models.TextField(verbose_name="Контент иконки", null=True, blank=True)
    description = RichTextField(verbose_name="Описание", blank=True)
    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0)

    class Meta:
        ordering = ("order",)
        verbose_name = "Назначение объекта собственности"
        verbose_name_plural = "Назначения объектов собственности"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        if self.icon:
            with default_storage.open(self.icon.name) as icon_file:
                icon_content = icon_file.read()
                if isinstance(icon_content, bytes):
                    icon_content = icon_content.decode("utf-8")
                icon_content.replace("\n", "").replace("b'", "")
                if icon_content.endswith("'"):
                    icon_content = icon_content[:-1]
            PropertyPurpose.objects.filter(id=self.id).update(icon_content=icon_content)
            self.refresh_from_db()
