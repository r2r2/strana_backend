from django.db import models
from ajaximage.fields import AjaxImageField


class FurnishKitchen(models.Model):
    """
    Отделка кухни
    """

    name = models.CharField(verbose_name="Название", max_length=200)
    tech_name = models.CharField(verbose_name="Техническое название", max_length=200)
    description = models.TextField(verbose_name="Описание", blank=True)
    vr_link = models.URLField(verbose_name="Ссылка VR-тур", max_length=200, null=True, blank=True)
    order = models.PositiveIntegerField(verbose_name="Порядок", default=0, db_index=True)
    video = models.URLField(verbose_name="Видео / Ссылка", null=True, blank=True)
    video_preview = AjaxImageField(verbose_name="Видео / Превью", null=True, blank=True)
    video_description = models.TextField(verbose_name="Подпись к Видео / Превью", blank=True)

    def __str__(self) -> str:
        return self.tech_name

    class Meta:
        verbose_name = "Отделка кухни"
        verbose_name_plural = "Отделки кухни"
        ordering = ("order",)
