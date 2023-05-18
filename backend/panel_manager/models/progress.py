from django.db import models

from common.models import MultiImageMeta, Spec
from ..const import ProgressMonth, ProgressQuarter
from ..querysets import ProgressQuerySet


class Progress(models.Model, metaclass=MultiImageMeta):
    """
    Ход строительства
    """

    IMAGE_WIDTH = 664
    IMAGE_HEIGHT = 664

    objects = ProgressQuerySet.as_manager()

    year = models.PositiveIntegerField(verbose_name="Год")
    month = models.CharField(verbose_name="Месяц", max_length=20, choices=ProgressMonth.choices)
    quarter = models.PositiveSmallIntegerField(
        verbose_name="Квартал", choices=ProgressQuarter.choices
    )
    active = models.BooleanField(verbose_name="Активно", default=True)
    image = models.ImageField(verbose_name="Изображение", upload_to="pr/pr/i")
    project = models.ForeignKey(
        verbose_name="Проект",
        to="projects.Project",
        on_delete=models.CASCADE,
        related_name="progress_project",
    )
    order = models.PositiveSmallIntegerField(verbose_name="Порядок")

    image_map = {
        "image_display": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT),
        "image_preview": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, True),
    }

    def __str__(self) -> str:
        return f"Ход строительства {self.project.name} {self.month} {self.year} года"

    class Meta:
        verbose_name = "Ход строительства"
        verbose_name_plural = "Ходы строительства"
        ordering = ("order",)
