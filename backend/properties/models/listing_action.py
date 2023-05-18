from django.db import models
from common.models import MultiImageMeta, Spec


class ListingAction(models.Model, metaclass=MultiImageMeta):
    """ Модель акции в листиеге квартир """

    IMAGE_WIDTH = 400
    IMAGE_HEIGHT = 600

    uptitle = models.CharField(verbose_name="Над заголовком", max_length=50, blank=True)
    title = models.CharField(verbose_name="Заголовок", max_length=128)
    description = models.TextField(verbose_name="Описание", blank=True)
    city = models.ForeignKey(
        verbose_name="Город", to="cities.City", blank=True, null=True, on_delete=models.SET_NULL
    )
    order = models.PositiveSmallIntegerField(verbose_name="Очередность", default=0)
    image = models.ImageField(
        verbose_name="Изображенине",
        blank=True,
        upload_to="p/la",
        help_text=f"Ширина: {IMAGE_WIDTH}, высота: {IMAGE_HEIGHT}",
    )
    button_name = models.CharField("Название кнопки", blank=True, max_length=64)
    button_link = models.CharField("Ссылка кнопки", blank=True, max_length=255)

    image_map = {
        "image_display": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "image_preview": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, True),
    }

    class Meta:
        ordering = ("order",)
        verbose_name = "Акция в листинге квартир"
        verbose_name_plural = "Акции в листинге квартир"

    def __str__(self):
        return self.title
