# pylint: disable=no-member
from typing import Optional
from uuid import UUID, uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _


class IsConType(models.TextChoices):
    YES: str = "yes", _("Да")
    NO: str = "no", _("Нет")
    SKIP: str = "skip", _("Не важно")


class UniqueValueType(models.TextChoices):
    UNIQUE = "unique", _("Уникален")
    NOT_UNIQUE = "not_unique", _("Не уникален")
    CAN_DISPUTE = "can_dispute", _("Закреплен, но можно оспорить")


class CitiesThrough(models.Model):
    city = models.ForeignKey(verbose_name="Город", to="cities.Cities", on_delete=models.CASCADE, unique=False)
    term = models.ForeignKey(to="users.CabinetChecksTerms", on_delete=models.CASCADE, related_name="city")

    def __str__(self, *args, **kwargs):
        return self.city.name

    class Meta:
        managed = False
        db_table = "users_checks_terms_cities"
        verbose_name = "Город"
        verbose_name_plural = "Города"
        unique_together = (('city', 'term'),)


class PipelinesThrough(models.Model):
    pipeline = models.ForeignKey(verbose_name="Воронка", to="amocrm.AmocrmPipeline", on_delete=models.CASCADE, unique=False)
    term = models.ForeignKey(to="users.CabinetChecksTerms", on_delete=models.CASCADE, related_name="pipeline")

    class Meta:
        managed = False
        db_table = "users_checks_terms_pipelines"
        verbose_name = "Воронка"
        verbose_name_plural = "Воронки"
        unique_together = (('pipeline', 'term'),)


class StatusesThrough(models.Model):
    status = models.ForeignKey(verbose_name="Статус", to="amocrm.AmocrmStatus", on_delete=models.CASCADE, unique=False)
    term = models.ForeignKey(to="users.CabinetChecksTerms", on_delete=models.CASCADE, related_name="status")

    class Meta:
        managed = False
        db_table = "users_checks_terms_statuses"
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"
        unique_together = (('status', 'term'),)


class CabinetChecksTerms(models.Model):
    """
    Условия проверки на уникальность
    """

    uid: UUID = models.UUIDField(verbose_name="ID", default=uuid4, primary_key=True, unique=True, editable=False)
    cities = models.ManyToManyField(verbose_name="Города", to="cities.Cities", through="CitiesThrough",
                                    blank=True, through_fields=("term", "city"))
    pipelines = models.ManyToManyField(verbose_name="Воронки", to="amocrm.AmocrmPipeline", through="PipelinesThrough",
                                       blank=True, through_fields=("term", "pipeline"))
    statuses = models.ManyToManyField(verbose_name="Статусы", to="amocrm.AmocrmStatus", through="StatusesThrough",
                                      blank=True, through_fields=("term", "status"))
    is_agent: str = models.CharField(verbose_name="Есть агент", choices=IsConType.choices, max_length=10, null=False)
    more_days: Optional[int] = models.IntegerField(verbose_name="Больше скольки дней сделка находится в статусе",
                                                   null=True, blank=True)
    less_days: Optional[int] = models.IntegerField(verbose_name="Меньше скольки дней сделка находится в статусе",
                                                   null=True, blank=True)
    is_assign_agency_status: str = models.CharField(verbose_name="Была ли сделка в статусе 'Фиксация за АН'",
                                                    choices=IsConType.choices, max_length=10, null=False,
                                                    default=IsConType.SKIP)
    priority: int = models.IntegerField(verbose_name="Приоритет", null=False)
    unique_value: str = models.CharField(verbose_name="Статус уникальности",
                                         choices=UniqueValueType.choices, max_length=30, null=False)

    def _cities(self):
        return list(self.cities.values_list("name", flat=True))
    _cities.short_description = 'Города'

    class Meta:
        managed = False
        db_table = "users_checks_terms"
        verbose_name = "Условие проверки"
        verbose_name_plural = "Условия проверки"
        ordering = ["priority"]
