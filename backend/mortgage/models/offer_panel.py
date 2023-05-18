from django.db import models
from django.contrib.postgres.fields import ArrayField
from cities.models import City
from common.fields import FloatRangeField, IntegerRangeField
from ..constants import MortgageType
from ..queryset import OfferQuerySet
from .bank import Bank
from .program import Program


class OfferPanel(models.Model):
    """
    Предложение по ипотеке для панели манаджера
    """

    objects = OfferQuerySet.as_manager()

    is_active = models.BooleanField(verbose_name="Активное", default=True)
    type = models.CharField(verbose_name="Тип", max_length=100, choices=MortgageType.choices)
    deposit = FloatRangeField(verbose_name="Первоначальный взнос", blank=True, null=True)
    rate = FloatRangeField(verbose_name="Процентная ставка", blank=True, null=True)
    term = FloatRangeField(verbose_name="Срок кредита", blank=True, null=True)
    amount = IntegerRangeField(verbose_name="Сумма кредита", blank=True, null=True)
    subs_rate = FloatRangeField(
        verbose_name="Процентная ставка (субсидированная ипотека)", blank=True, null=True
    )
    subs_term = FloatRangeField(
        verbose_name="Срок кредита (субсидированная ипотека)", blank=True, null=True
    )

    bank = models.ForeignKey(verbose_name="Банк", to=Bank, on_delete=models.CASCADE, null=True, blank=True)
    program = models.ForeignKey(
        verbose_name="Программа", to=Program, on_delete=models.CASCADE, null=True, blank=True
    )
    city = models.ForeignKey(
        verbose_name="Город", to=City, on_delete=models.CASCADE, null=True, blank=True
    )
    projects = models.ManyToManyField(verbose_name="Проекты", to="projects.Project", blank=True)

    order = models.PositiveIntegerField(verbose_name="Порядок", default=0, db_index=True)

    dvizh_ids = ArrayField(
        verbose_name="id предложения в Движ.API",
        base_field=models.PositiveIntegerField(),
        default=list,
        null=True, blank=True
    )
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Предложение {self.id}"

    class Meta:
        verbose_name = "Предложение по ипотеке для панели"
        verbose_name_plural = "Предложения по ипотеке для панели"
        get_latest_by = "rate"
        ordering = ("order",)
