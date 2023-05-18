from django.db import models

from common.fields import ChoiceArrayField
from properties.constants import PropertyType
from ..constants import FeatureType
from ..querysets import FeatureQuerySet


class Feature(models.Model):
    """Модель особенности объекта собственности"""

    objects = FeatureQuerySet.as_manager()

    name = models.CharField(verbose_name="Название", max_length=64)
    kind = models.CharField(
        verbose_name="Тип", choices=FeatureType.choices, default=FeatureType.FACING, max_length=48
    )
    property_kind = ChoiceArrayField(
        verbose_name="Типы недвижимости",
        base_field=models.CharField(choices=PropertyType.choices, max_length=20),
        default=list,
    )
    cities = models.ManyToManyField(verbose_name="Города", to="cities.City", blank=True)
    filter_show = models.BooleanField(verbose_name="Отображать в фильтре листинга", default=True)
    main_filter_show = models.BooleanField(
        verbose_name="Отображать в фильтре на главной", default=False
    )
    lot_page_show = models.BooleanField(verbose_name="Отображать на странице лота", default=True)
    icon_show = models.BooleanField(verbose_name="Отображать иконку", default=False)
    icon_flats_show = models.BooleanField(verbose_name="Отображать на странице flats", default=False)
    icon = models.FileField(verbose_name="Иконка", blank=True, upload_to="p/f")
    icon_flats_show = models.BooleanField(verbose_name="Отображать на странице flats", default=False)
    icon_hypo = models.FileField(
        verbose_name="Картинка для тултипа в фильтре",
        blank=True,
        upload_to="p/ph",
        help_text="Загружать изображение около 300x250px",
    )
    icon_flats = models.FileField(verbose_name="Иконка для страницы flats", blank=True, upload_to="p/f")
    description = models.TextField(verbose_name="Описание", blank=True)
    order = models.PositiveSmallIntegerField("Очередность", default=0, db_index=True)
    is_button = models.BooleanField("Выводить кнопкой", default=False)

    class Meta:
        ordering = ("order",)
        verbose_name = "Особенность объекта собственнсти"
        verbose_name_plural = "Особенности объектов собственности"

    def __str__(self):
        return self.name
