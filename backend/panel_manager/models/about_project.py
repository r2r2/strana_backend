from ckeditor.fields import RichTextField
from django.db import models
from django.utils.safestring import mark_safe
from solo.models import SingletonModel

from common.fields import PpoiField
from common.models import MultiImageMeta, Spec
from projects.models import Project


class AboutProject(SingletonModel):
    class Meta:
        verbose_name = "О проекте"
        verbose_name_plural = "О проекте"


class AboutProjectParametrs(models.Model):
    PARAMS = (
        (0, "Оранжевый заголовок"),
        (1, "Обычный заголовок"),
    )
    about_project = models.ForeignKey(
        AboutProject, models.CASCADE, verbose_name="Страница о проекта"
    )
    title = RichTextField("Заголовок", blank=True)
    description = RichTextField("Описание", blank=True)

    type = models.IntegerField("Тип параметра", default=1, choices=PARAMS)

    order = models.PositiveIntegerField("Очередность", default=0)

    class Meta:
        verbose_name = "Параметр"
        verbose_name_plural = "Параметры"
        ordering = ("order",)


class AboutProjectGalleryCategory(models.Model, metaclass=MultiImageMeta):
    """Категории галлерей"""

    PLAN_WIDTH = 300
    PLAN_HEIGHT = 300

    project = models.ForeignKey(Project, models.CASCADE, verbose_name="Проект")
    name = models.CharField("Наименование", max_length=200)
    icon = models.ImageField("Иконка", upload_to="p/ap/i", blank=True, null=True)
    description = RichTextField("Описание", blank=True)

    order = models.PositiveIntegerField("Очередность", default=0)

    image_map = {
        "icon_display": Spec("icon", PLAN_WIDTH, PLAN_HEIGHT),
        "icon_preview": Spec("icon", PLAN_WIDTH, PLAN_HEIGHT, True),
    }

    class Meta:
        verbose_name = "Категории галлерей"
        verbose_name_plural = "Категории галлерей"
        ordering = ("order",)

    def __str__(self):
        return f"{self.project} = {self.name}"


class AboutProjectGallery(models.Model, metaclass=MultiImageMeta):
    """Галлерея о проекте"""

    PLAN_WIDTH = 2732
    PLAN_HEIGHT = 2048

    category = models.ForeignKey(
        AboutProjectGalleryCategory, models.CASCADE, verbose_name="Категория"
    )

    image = models.ImageField("Изображение", upload_to="pm/apg/i", blank=True)
    video = models.FileField("Видео", upload_to="pm/apg/v", blank=True)
    on_map = models.BooleanField("Ссылка на карту", default=False)
    video_url = models.TextField("URL для видео", blank=True)
    tour_url = models.TextField("URL для 3Д тура", blank=True)
    description = RichTextField("Описание", blank=True)

    order = models.PositiveIntegerField("Очередность", default=0)

    image_map = {
        "image_display": Spec("image", PLAN_WIDTH, PLAN_HEIGHT),
        "image_preview": Spec("image", PLAN_WIDTH, PLAN_HEIGHT, True),
    }

    class Meta:
        verbose_name = "Галлерея о проекте"
        verbose_name_plural = "Галлереи о проекте"
        ordering = ("order",)

    def __str__(self):
        return f"{self.category} #{self.id}"

    @property
    def announcement_image(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" width="150" height="100"/>')


class PinsAboutProjectGallery(models.Model):
    """Точки на изображении"""

    image = models.ForeignKey(AboutProjectGallery, models.CASCADE, verbose_name="Изображение")

    pin = PpoiField("Точка на рендере", source="image.image", max_length=8, blank=True)

    description = RichTextField("Описание", blank=True)
    open = models.BooleanField("Открыт сразу", default=False)

    class Meta:
        verbose_name = "Точка на изображении"
        verbose_name_plural = "Точки на изображении"

    def __str__(self):
        return f"{self.image} #{self.id}"
