from ajaximage.fields import AjaxImageField
from django.db import models
from common.models import MultiImageMeta, Spec
from ..constants import ProjectAdvantageSlideChoices
from .project_advantage import ProjectAdvantage


class ProjectAdvantageSlide(models.Model, metaclass=MultiImageMeta):
    """
    Слайд преимущества
    """

    WIDTH = 1560
    HEIGHT = 1200
    WIDTH_MOB = 390
    HEIGHT_MOB = 350
    WIDTH_TAB = 768
    HEIGHT_TAB = 368

    image = AjaxImageField(
        verbose_name="Изображение", upload_to="p/advantage",
        help_text=f"Выс.- {HEIGHT}, Шир.- {WIDTH}",
    )
    image_mob = AjaxImageField(
        verbose_name="Изображение (моб.)", upload_to="p/advantage", blank=True,
        help_text=f"Выс.- {HEIGHT_MOB}, Шир.- {WIDTH_MOB}",
    )
    image_laptop = AjaxImageField(
        verbose_name="Изображение (планшет.)", upload_to="p/advantage", blank=True,
        help_text=f"Выс.- {HEIGHT_TAB}, Шир.- {WIDTH_TAB}",
    )

    project_advantage = models.ForeignKey(
        verbose_name="Преимущество",
        to=ProjectAdvantage,
        on_delete=models.CASCADE,
        related_name="advantage_slides",
    )
    description = models.TextField(verbose_name="Опиание изображения", blank=True, max_length=30)
    image_position = models.CharField(
        verbose_name="Положение изображения",
        max_length=20,
        choices=ProjectAdvantageSlideChoices.choices,
        default=ProjectAdvantageSlideChoices.CENTER,
    )

    order = models.PositiveSmallIntegerField(verbose_name="Порядок")

    image_map = {
        "image_display": Spec(source="image", width=WIDTH, height=HEIGHT),
        "image_preview": Spec(source="image", width=WIDTH, height=HEIGHT, blur=True),
        "image_mob_display": Spec(source="image_mob", width=WIDTH_MOB, height=HEIGHT_MOB),
        "image_mob_preview": Spec(
            source="image_mob", width=WIDTH_MOB, height=HEIGHT_MOB, blur=True
        ),
        "image_laptop_display": Spec(source="image_laptop", width=WIDTH_TAB, height=HEIGHT_TAB),
        "image_laptop_preview": Spec(
            source="image_laptop", width=WIDTH_TAB, height=HEIGHT_TAB, blur=True
        ),
    }

    class Meta:
        verbose_name = "Слайд преимущества"
        verbose_name_plural = "Слайды преимуществ"
        ordering = ("order",)

    def __str__(self):
        return f"Слайд №{self.order}"
