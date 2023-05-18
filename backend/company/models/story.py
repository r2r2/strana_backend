from ajaximage.fields import AjaxImageField
from django.db import models
from ckeditor.fields import RichTextField
from common.models import OrderedImage, Spec, MultiImageMeta


class Story(models.Model, metaclass=MultiImageMeta):
    """ Модель истории о компании """

    WIDTH = 215
    HEIGHT = 276

    name = models.CharField("Название", max_length=32)
    file = AjaxImageField("Обложка", blank=True, upload_to="c/s")
    order = models.PositiveSmallIntegerField("Порядок", default=0)
    about_section = models.ForeignKey(
        "company.AboutPage", verbose_name="Страница о компании", on_delete=models.CASCADE
    )

    image_map = {
        "file_display": Spec(source="file", width=WIDTH, height=HEIGHT, default="png"),
        "file_preview": Spec(source="file", width=WIDTH, height=HEIGHT, blur=True),
    }

    class Meta:
        ordering = ("order",)
        verbose_name = "История о компании"
        verbose_name_plural = "Истории о компании"

    def __str__(self):
        return self.name


class StoryImage(OrderedImage):
    """ Модель изображения истории о компании"""

    upload_to = "c/s/si"
    WIDTH = 840
    HEIGHT = 664

    text = RichTextField("Текст", blank=True)
    story = models.ForeignKey(
        Story, verbose_name="История", on_delete=models.CASCADE, related_name="images"
    )

    image_map = {
        "file_display": Spec(source="file", width=WIDTH, height=HEIGHT),
        "file_preview": Spec(source="file", width=WIDTH, height=HEIGHT, blur=True),
    }

    class Meta:
        ordering = ("order",)
        verbose_name = "Изображение истории о компании"
        verbose_name_plural = "Изображения истории о компании"

    def __str__(self) -> str:
        return str(self.order)
