from django.db import models

from common.models import OrderedImage
from ..constants import ProjectLabelShapeChoices


class ProjectLabel(OrderedImage):
    """Лейбл в шапке проекта"""

    upload_to = "p/label"

    name = models.CharField("Название", max_length=64)
    description = models.CharField("Описание", max_length=300, blank=True)
    display_main = models.BooleanField("Выводить на главной", default=False)
    display_slider = models.BooleanField(
        "Выводить в слайдере", help_text="В шапке на странице проекта", default=False
    )
    link = models.CharField(verbose_name="Ссылка", blank=True, max_length=200)
    shape = models.CharField(
        verbose_name="Форма лейбла",
        max_length=64,
        choices=ProjectLabelShapeChoices.choices,
        default=ProjectLabelShapeChoices.SQUARE,
    )
    projects = models.ManyToManyField("projects.Project", verbose_name="Проекты")

    class Meta:
        ordering = ("order",)
        verbose_name = "Лейбл проектов"
        verbose_name_plural = "Лейблы проектов"

    def __str__(self):
        return self.name
