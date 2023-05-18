from ajaximage.fields import AjaxImageField
from ckeditor.fields import RichTextField

from django.db import models
from common.models import MultiImageMeta, Spec


class JobDescription(models.Model, metaclass=MultiImageMeta):

    WIDTH = 1200
    HEIGHT = 1560

    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0)
    title = models.CharField(verbose_name="Заголовок", max_length=200)
    description = RichTextField(
        verbose_name="Описание", null=True, blank=True,
    )
    image = AjaxImageField(
        verbose_name="Изображение", upload_to="f/jd", null=True
    )
    furnish = models.ForeignKey(
        to="properties.Furnish", verbose_name="Отделка",
        on_delete=models.CASCADE
    )
    image_map = {
        "image_display": Spec(source="image", width=WIDTH, height=HEIGHT),
        "image_preview": Spec(source="image", width=WIDTH, height=HEIGHT, blur=True),
    }

    class Meta:
        verbose_name_plural = verbose_name = "Описание работы"
        ordering = ("order",)


class JobDescriptionKitchen(models.Model, metaclass=MultiImageMeta):

    WIDTH = 1200
    HEIGHT = 1560

    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0)
    title = models.CharField(verbose_name="Заголовок", max_length=200)
    description = RichTextField(
        verbose_name="Описание", null=True, blank=True,
    )
    image = AjaxImageField(
        verbose_name="Изображение", upload_to="f/kitchen/jd", null=True
    )
    furnish = models.ForeignKey(
        to="properties.FurnishKitchen", verbose_name="Отделка",
        on_delete=models.CASCADE
    )
    image_map = {
        "image_display": Spec(source="image", width=WIDTH, height=HEIGHT),
        "image_preview": Spec(source="image", width=WIDTH, height=HEIGHT, blur=True),
    }

    class Meta:
        verbose_name_plural = verbose_name = "Описание работы для кухни"
        ordering = ("order",)


class JobDescriptionFurniture(models.Model, metaclass=MultiImageMeta):

    WIDTH = 1200
    HEIGHT = 1560

    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0)
    title = models.CharField(verbose_name="Заголовок", max_length=200)
    description = RichTextField(
        verbose_name="Описание", null=True, blank=True,
    )
    image = AjaxImageField(
        verbose_name="Изображение", upload_to="f/furniture/jd", null=True
    )
    furnish = models.ForeignKey(
        to="properties.FurnishFurniture", verbose_name="Мебель",
        on_delete=models.CASCADE
    )
    image_map = {
        "image_display": Spec(source="image", width=WIDTH, height=HEIGHT),
        "image_preview": Spec(source="image", width=WIDTH, height=HEIGHT, blur=True),
    }

    class Meta:
        verbose_name_plural = verbose_name = "Описание работы для мебели"
        ordering = ("order",)