from django.db import models


class TemplateContent(models.Model):
    """
    Статический контент шаблонов писем.
    """

    description = models.TextField(
        verbose_name="Описание",
    )
    slug = models.CharField(
        max_length=50,
        verbose_name="Слаг (для работы с бекендом)",
        blank=True,
        null=True,
    )
    file = models.FileField(
        verbose_name="Файл",
        max_length=500,
        upload_to="d/i/f",
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return self.description

    class Meta:
        managed = False
        db_table = "notifications_template_content"
        verbose_name = "Контент шаблонов писем"
        verbose_name_plural = "4.10. [Общее] Контент шаблонов писем"
