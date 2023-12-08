from django.db import models


class NewsSettings(models.Model):
    """
    Настройки новостей.
    """

    default_image_preview = models.FileField(verbose_name="Изображение (превью) по умолчанию")
    default_image = models.FileField(verbose_name="Изображение по умолчанию")

    def __str__(self) -> str:
        return "Настройки новостей"

    class Meta:
        managed = False
        db_table = "news_news_settings"
        verbose_name = verbose_name_plural = "20.4. Настройки"
