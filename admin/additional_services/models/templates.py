from django.db import models


class AdditionalServiceTemplate(models.Model):
    """
    Шаблоны доп услуг
    """

    title: str = models.CharField(verbose_name="Название", max_length=150)
    description: str = models.TextField(verbose_name="Текст")
    button_text: str = models.TextField(verbose_name="Текст кнопки")
    slug: str = models.CharField(
        max_length=50, verbose_name="slug", null=True, unique=True
    )

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = "additional_services_templates"
        verbose_name = "шаблон"
        verbose_name_plural = "17.6. [Справочник] Текст пустой страницы списка доп. услуг"
