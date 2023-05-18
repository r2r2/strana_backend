from django.db import models
from ajaximage.fields import AjaxImageField
from ckeditor.fields import RichTextField
from common.models import OrderedImage, Spec


class ProjectIdeology(models.Model):
    """
    Идеология проекта
    """

    text_1 = RichTextField(verbose_name="Текст 1", blank=True)
    text_2 = RichTextField(verbose_name="Текст 2", blank=True)
    image_1 = AjaxImageField(verbose_name="Изображение 1", null=True, blank=True)
    image_2 = AjaxImageField(verbose_name="Изображение 1", null=True, blank=True)
    video_link_1 = models.URLField(verbose_name="Ссылка на видео 1", blank=True)
    video_preview_1 = AjaxImageField(verbose_name="Превью видео 1", null=True, blank=True)
    video_link_2 = models.URLField(verbose_name="Ссылка на видео 2", blank=True)
    video_preview_2 = AjaxImageField(verbose_name="Превью видео 2", null=True, blank=True)
    button_text = models.CharField(verbose_name="Текст кнопки", max_length=100, blank=True)
    button_link = models.URLField(verbose_name="Ссылка на кнопке", blank=True)

    def __str__(self) -> str:
        return f"Идеология проекта {self.id}"

    class Meta:
        verbose_name = "Идеология проекта"
        verbose_name_plural = "Идеологии проекта"


class ProjectIdeologyCard(OrderedImage):
    """
    Карточка идеологии проекта
    """

    upload_to = "p/ideology/slides"
    WIDTH = 738
    HEIGHT = 484

    title = models.CharField(verbose_name="Заголовок", max_length=200, blank=True)
    text = RichTextField(verbose_name="Текст", blank=True)

    ideology = models.ForeignKey(
        verbose_name="Идеология",
        to=ProjectIdeology,
        on_delete=models.CASCADE,
        related_name="ideology_cards",
    )

    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0, db_index=True)

    image_map = {
        "file_display": Spec(source="file", width=WIDTH, height=HEIGHT),
        "file_preview": Spec(source="file", width=WIDTH, height=HEIGHT, blur=True),
    }

    def __str__(self) -> str:
        return f"Карточка идеологии {self.id}"

    class Meta:
        verbose_name = "Карточка идеологии проекта"
        verbose_name_plural = "Карточки идеологии проекта"
        ordering = ("order",)
