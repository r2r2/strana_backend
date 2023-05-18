from ckeditor.fields import RichTextField
from django.db import models
from solo.models import SingletonModel

from common.fields import PpoiField


class OurProjects(SingletonModel):
    """Наши проекты"""

    maps = models.ImageField("Изображение карты", upload_to="p/ac/m", blank=True)
    indicators_one_title = RichTextField("Заголовок первого показателя", blank=True)
    indicators_one_description = RichTextField("Описание первого показателя", blank=True)
    indicators_two_title = RichTextField("Заголовок второго показателя", blank=True)
    indicators_two_description = RichTextField("Описание второго показателя", blank=True)

    class Meta:
        verbose_name = "Наши проекты"
        verbose_name_plural = "Наши проекты"

    def __str__(self):
        return "Наши проекты"


class StageProjects(models.Model):
    """Стадия проекта"""

    title = models.CharField("Название", max_length=200)
    color = models.CharField("Цвет", max_length=200, default="#FFFFFF")
    order = models.PositiveSmallIntegerField("Очередность", default=0)
    pin_image = models.FileField("Изображение пина", upload_to="p/sp/pi", blank=True)

    class Meta:
        verbose_name = "Стадия проекта"
        verbose_name_plural = "Стадия проекта"
        ordering = ("order",)

    def __str__(self):
        return self.title


class ProjectsForMap(models.Model):
    """Проекты  на карте"""

    stage = models.ForeignKey(StageProjects, models.CASCADE, verbose_name="Стадия проекта")
    our_project = models.ForeignKey(
        OurProjects,
        models.CASCADE,
        default=OurProjects.singleton_instance_id,
        verbose_name="Наш проект",
    )

    title = RichTextField("Заголовок", blank=True)
    description = RichTextField("Описание", blank=True)
    point = PpoiField("Координаты точки", source="our_project.maps", max_length=100, blank=True)

    order = models.PositiveSmallIntegerField("Очередность", default=0)

    class Meta:
        verbose_name = 'Проект в разделе "О компании"'
        verbose_name_plural = 'Проекты в разделе "О компании"'
        ordering = ("order",)

    def __str__(self):
        return self.title
