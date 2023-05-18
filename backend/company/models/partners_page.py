from ckeditor.fields import RichTextField
from django.db import models
from solo.models import SingletonModel
from ..constants import BlockType


class PartnersPage(SingletonModel):
    """
    Страница партнеров
    """

    text_1 = RichTextField(verbose_name="Описание 1", null=True, blank=True)
    text_2 = RichTextField(verbose_name="Описание 2", null=True, blank=True)
    partners = models.CharField(verbose_name="Партнеры", max_length=30, null=True, blank=True)
    partners_description = RichTextField(
        verbose_name="Описание партнеров", max_length=1000, null=True, blank=True
    )

    def __str__(self) -> str:
        return self._meta.verbose_name

    class Meta:
        verbose_name = "Страница партнерам"
        verbose_name_plural = "Страница партнерам"


class PartnersPageBlock(models.Model):
    """
    Блок страницы партнеров
    """

    title = models.CharField(verbose_name="Заголовок", max_length=200, blank=True)
    link_text = models.CharField(verbose_name="Текст ссылки", max_length=200, blank=True)
    link_url = models.CharField(verbose_name="URL ссылки", max_length=2000, blank=True)

    block_type = models.CharField(
        verbose_name="Тип блока", choices=BlockType.choices, max_length=300, blank=True
    )

    page = models.ForeignKey(verbose_name="Страница", to=PartnersPage, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Блок страницы партнеров"
        verbose_name_plural = "Блоки страницы партнеров"
