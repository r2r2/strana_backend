from django.db import models
from ajaximage.fields import AjaxImageField
from ckeditor.fields import RichTextField

from ..constants import IMAGE_WIDTH, IMAGE_HEIGHT
from cities.models import City
from projects.models import Project


class PopUpTag(models.Model):
    tag = models.CharField(verbose_name="Тэг", max_length=200, unique=True)
    name = models.CharField(verbose_name="Название Поп-апа", max_length=200)

    def __str__(self):
        return f'{self.name}'


class PopUpInfo(models.Model):
    title = models.CharField(verbose_name="Заголовок", max_length=200)
    subtitle = models.CharField(verbose_name="Подзаголовок", max_length=200, blank=True)
    description = RichTextField(verbose_name="Описание", blank=True)
    image = AjaxImageField(
        verbose_name="Изображение",
        upload_to="f/i",
        null=True,
        blank=True,
        help_text=f"шир. - {IMAGE_WIDTH}, выс. - {IMAGE_HEIGHT}",
    )
    alt = models.CharField(verbose_name="Подпись к картинке", max_length=200, blank=True)
    city = models.ManyToManyField(City, blank=True, verbose_name='Город')
    project = models.ManyToManyField(Project, blank=True, verbose_name='Проекты')
    pop_up_tag = models.ForeignKey(
        verbose_name="Pop up tag", to="PopUpTag", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f'{self.title}'
