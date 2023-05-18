from colorful.fields import RGBColorField
from django.db import models

from ..querysets import SpecialOfferQuerySet
from ..constants import DiscountUnit


class SpecialOffer(models.Model):
    """ Модель акции объекта собственности """

    objects = SpecialOfferQuerySet.as_manager()

    name = models.CharField(
        verbose_name="Название", max_length=120, blank=True,
        help_text="Заполняется вручную. Название чек-бокса в фильтре и акции на странице квартиры"
    )
    is_active = models.BooleanField(verbose_name="Активна", default=False)
    is_display = models.BooleanField(
        verbose_name="Отображать на сайте", default=False,
        help_text="Отображение чек-бокса в фильтре и акции на странице квартиры"
    )
    color = RGBColorField(verbose_name="Цвет", blank=True)
    icon = models.FileField(
        verbose_name="Иконка", blank=True, upload_to="spo/f",
        help_text="Отображается на странице квартиры"
    )
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    description_active = models.BooleanField(verbose_name="Описание активно", default=True)
    start_date = models.DateTimeField(verbose_name="Дата начала", blank=True, null=True)
    finish_date = models.DateTimeField(verbose_name="Дата окончания", blank=True, null=True)
    discount_active = models.BooleanField(verbose_name="Скидка активна", default=False)
    discount_value = models.PositiveIntegerField(verbose_name="Значение скидки", default=0)
    discount_type = models.CharField(verbose_name="Тип скидки", blank=True, max_length=120)
    discount_unit = models.CharField(
        verbose_name="Единицы измерения скидки", blank=True, max_length=32, choices=DiscountUnit.choices
    )
    discount_description = models.TextField(verbose_name="Описание скидки", blank=True)
    badge_icon = models.CharField(verbose_name="Иконка бейджа", blank=True, max_length=120)
    badge_label = models.CharField(verbose_name="Название акции в PB", blank=True, max_length=120)

    properties = models.ManyToManyField(
        verbose_name="Объекты собственности", blank=True, to="properties.Property"
    )

    is_update_profit = models.BooleanField(verbose_name="Выгрузка из profit-a", default=True)

    class Meta:
        verbose_name = "Акция объектов собственности"
        verbose_name_plural = "Акции объектов собственности"

    def __str__(self):
        return self.name or self.badge_label
