from django.db import models
from common.models import MultiImageMeta, Spec


class ProjectFeature(models.Model, metaclass=MultiImageMeta):
    """
    Особенность проекта
    """

    WIDTH = 486
    HEIGHT = 464

    title = models.CharField(verbose_name="Заголовок", max_length=100)
    text = models.TextField(verbose_name="Текст", max_length=500, null=True, blank=True)
    image = models.ImageField(verbose_name="Изображение", upload_to="p/pf/i", null=True, blank=True)

    project = models.ForeignKey(
        verbose_name="Проект", to="projects.Project", on_delete=models.CASCADE
    )

    order = models.PositiveSmallIntegerField(verbose_name="Порядок")

    image_map = {
        "image_display": Spec(source="image", default="png", width=WIDTH, height=HEIGHT),
        "image_preview": Spec(source="image", default="png", width=WIDTH, height=HEIGHT, blur=True),
    }

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Особенность проекта"
        verbose_name_plural = "Особенности проекта"
        ordering = ("order",)
