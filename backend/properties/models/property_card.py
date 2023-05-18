from ckeditor.fields import RichTextField
from django.db import models
from common.models import MultiImageMeta, Spec
from properties.constants import PropertyCardKind


class PropertyCard(models.Model, metaclass=MultiImageMeta):
    """
    Карточка подборщика
    """

    IMAGE_WIDTH = 960
    IMAGE_HEIGHT = 584

    uptitle = models.CharField(verbose_name="Над заголовком", max_length=50)
    title = models.CharField(verbose_name="Заголовок", max_length=200)
    text = RichTextField(verbose_name="Текст", max_length=1000)
    image = models.ImageField(verbose_name="Изображение", upload_to="p/pc/i")
    link = models.URLField(verbose_name="Ссылка", max_length=200, null=True, blank=True)
    kind = models.CharField(verbose_name="Тип", choices=PropertyCardKind.choices, max_length=15)

    image_map = {
        "image_display": Spec(source="image", width=IMAGE_WIDTH, height=IMAGE_HEIGHT),
        "image_preview": Spec(source="image", width=IMAGE_WIDTH, height=IMAGE_HEIGHT, blur=True),
    }

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Карточка подборщика"
        verbose_name_plural = "Карточки подборщика"
