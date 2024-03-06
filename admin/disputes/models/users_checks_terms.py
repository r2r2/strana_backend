# pylint: disable=no-member
from typing import Optional
from uuid import UUID, uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _


class IsConType(models.TextChoices):
    YES: str = "yes", _("Да")
    NO: str = "no", _("Нет")
    SKIP: str = "skip", _("Не важно")


class CitiesThrough(models.Model):
    city = models.ForeignKey(verbose_name="Город", to="references.Cities", on_delete=models.CASCADE, unique=False)
    term = models.ForeignKey(to="disputes.CabinetChecksTerms", on_delete=models.CASCADE, related_name="city")

    def __str__(self, *args, **kwargs):
        return self.city.name

    class Meta:
        managed = False
        db_table = "users_checks_terms_cities"
        verbose_name = "Город"
        verbose_name_plural = "Города"
        unique_together = (('city', 'term'),)


class PipelinesThrough(models.Model):
    pipeline = models.ForeignKey(verbose_name="Воронка", to="booking.AmocrmPipeline", on_delete=models.CASCADE, unique=False)
    term = models.ForeignKey(to="disputes.CabinetChecksTerms", on_delete=models.CASCADE, related_name="pipeline")

    class Meta:
        managed = False
        db_table = "users_checks_terms_pipelines"
        verbose_name = "Воронка"
        verbose_name_plural = "Воронки"
        unique_together = (('pipeline', 'term'),)


class StatusesThrough(models.Model):
    status = models.ForeignKey(verbose_name="Статус", to="booking.AmocrmStatus", on_delete=models.CASCADE, unique=False)
    term = models.ForeignKey(to="disputes.CabinetChecksTerms", on_delete=models.CASCADE, related_name="status")

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
    cities = models.ManyToManyField(verbose_name="Города", to="references.Cities", through="CitiesThrough",
                                    blank=True, through_fields=("term", "city"))
    pipelines = models.ManyToManyField(verbose_name="Воронки", to="booking.AmocrmPipeline", through="PipelinesThrough",
                                       blank=True, through_fields=("term", "pipeline"))
    statuses = models.ManyToManyField(verbose_name="Статусы", to="booking.AmocrmStatus", through="StatusesThrough",
                                      blank=True, through_fields=("term", "status"))
    is_agent: str = models.CharField(verbose_name="Есть агент", choices=IsConType.choices, max_length=10, null=False)
    more_days: Optional[int] = models.IntegerField(
        verbose_name="Больше скольки дней сделка должна находиться в текущем статусе",
        null=True,
        blank=True,
    )
    less_days: Optional[int] = models.IntegerField(
        verbose_name="Меньше скольки дней сделка должна находиться в текущем статусе",
        null=True,
        blank=True,
    )
    is_assign_agency_status: str = models.CharField(verbose_name="Была ли сделка в статусе 'Фиксация за АН'",
                                                    choices=IsConType.choices, max_length=10, null=False,
                                                    default=IsConType.SKIP)
    assigned_to_agent: bool = models.BooleanField(
        verbose_name="Закреплен за проверяющим агентом",
        null=True,
        blank=True,
    )
    assigned_to_another_agent: bool = models.BooleanField(
        verbose_name="Закреплен за другим агентом проверяющего агентства",
        null=True,
        blank=True,
    )
    priority: int = models.IntegerField(
        verbose_name="Приоритет", null=False, help_text="Чем меньше приоритет тем раньше проверяется условие")
    send_admin_email: bool = models.BooleanField(
        verbose_name="Отправлять письмо администраторам при проверке клиента в данном статусе",
        default=False,
    )
    send_rop_email: bool = models.BooleanField(
        verbose_name="Отправлять письмо РОПам при проверке клиента в данном статусе",
        default=False,
    )
    unique_status: models.ForeignKey = models.ForeignKey(
        verbose_name="Статус уникальности",
        to="disputes.UniqueStatus",
        related_name="terms",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Определяет статус закрепления конкретной сделки, соответствующий описанным выше условиям. "
                  "Проверяется только при проверке на уникальность. Если хотя бы одна сделка клиента получает статус "
                  "“Неуникален” (или аналогичный ему) - проверка прекращается, "
                  "в противном случае проверяются все сделки клиента",
    )
    button: models.ForeignKey = models.ForeignKey(
        verbose_name="Кнопка",
        to="disputes.UniqueStatusButton",
        related_name="terms",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    comment = models.TextField(
        verbose_name="Комментарий",
        null=True,
        blank=True,
        help_text="Внутренний комментарий по назначению статуса",
    )

    def _cities(self):
        return list(self.cities.values_list("name", flat=True))
    _cities.short_description = 'Города'

    class Meta:
        managed = False
        db_table = "users_checks_terms"
        verbose_name = "Условие проверки"
        verbose_name_plural = "6.2. Условия проверки статуса уникальности"
        ordering = ["priority"]
