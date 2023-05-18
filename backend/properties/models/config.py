from solo.models import SingletonModel
from ckeditor.fields import RichTextField

from django.db import models


class PropertyConfig(SingletonModel):
    """ Модель настройки объектов собственности """

    lot_form_title = models.CharField(
        verbose_name="Заголовок формы на карточке лота", blank=True, max_length=128
    )
    lot_form_description = RichTextField(verbose_name="Описание формы на карточке лота", blank=True)

    class Meta:
        verbose_name = "Настройка объектов собственности"

    def __str__(self):
        return self._meta.verbose_name
