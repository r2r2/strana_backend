from django.db import models

from common.models import MultiImageMeta


class ProgressGallery(models.Model, metaclass=MultiImageMeta):
    """
    Галлерея хода строительства
    """

    progress = models.ForeignKey(
        verbose_name="Ход строительства", to="panel_manager.Progress", on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        verbose_name="Категория",
        to="panel_manager.ProgressCategory",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    buildings = models.ManyToManyField("buildings.Building", verbose_name="Корпусы", blank=True)

    image = models.ImageField("Изображение", upload_to="pm/pg/i", blank=True)
    video = models.FileField("Видео", upload_to="pm/pg/v", blank=True)
    video_url = models.TextField("URL для видео", blank=True)
    tour_url = models.TextField("URL для 3Д тура", blank=True)
    description = models.TextField("Описание", blank=True)

    order = models.PositiveSmallIntegerField(verbose_name="Порядок")

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        verbose_name = "Галлерея хода строительства"
        verbose_name_plural = "Галлереи ходов строительства"
        ordering = ("order",)
