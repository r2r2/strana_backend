from django.db import models
from django.utils.translation import gettext_lazy as _


class PinningStatusType(models.TextChoices):
    """
    Статус закрепления
    """
    PINNED: str = "pinned", _("Закреплен")
    NOT_PINNED: str = "not_pinned", _("Не закреплен")
    PARTIALLY_PINNED: str = "partially_pinned", _("Частично закреплен")


class PinningStatusCity(models.Model):
    """
    Промежуточная таблица для связи статуса закрепления и города
    """
    city = models.ForeignKey(verbose_name="Город", to="references.Cities", on_delete=models.CASCADE, unique=False)
    pinning = models.ForeignKey(to="disputes.PinningStatus", on_delete=models.CASCADE, related_name="city")

    def __str__(self, *args, **kwargs):
        return self.city.name

    class Meta:
        managed = False
        db_table = "users_pinning_status_cities"
        verbose_name = "Город"
        verbose_name_plural = "Города"
        unique_together = (('city', 'pinning'),)


class PinningStatusPipeline(models.Model):
    """
    Промежуточная таблица для связи статуса закрепления и воронки
    """
    pipeline = models.ForeignKey(verbose_name="Воронка", to="booking.AmocrmPipeline", on_delete=models.CASCADE, unique=False)
    pinning = models.ForeignKey(to="disputes.PinningStatus", on_delete=models.CASCADE, related_name="pipeline")

    class Meta:
        managed = False
        db_table = "users_pinning_status_pipelines"
        verbose_name = "Воронка"
        verbose_name_plural = "Воронки"
        unique_together = (('pipeline', 'pinning'),)


class PinningStatusStatus(models.Model):
    """
    Промежуточная таблица для связи статуса закрепления и статуса
    """
    status = models.ForeignKey(verbose_name="Статус", to="booking.AmocrmStatus", on_delete=models.CASCADE, unique=False)
    pinning = models.ForeignKey(to="disputes.PinningStatus", on_delete=models.CASCADE, related_name="status")

    class Meta:
        managed = False
        db_table = "users_pinning_status_statuses"
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"
        unique_together = (('status', 'pinning'),)


class PinningStatus(models.Model):
    """
    Статус закрепления
    """
    cities = models.ManyToManyField(
        verbose_name="Города",
        to="references.Cities",
        through="PinningStatusCity",
        blank=True,
        through_fields=("pinning", "city"),
    )
    pipelines = models.ManyToManyField(
        verbose_name="Воронки",
        to="booking.AmocrmPipeline",
        through="PinningStatusPipeline",
        blank=True,
        through_fields=("pinning", "pipeline"),
    )
    statuses = models.ManyToManyField(
        verbose_name="Статусы",
        to="booking.AmocrmStatus",
        through="PinningStatusStatus",
        blank=True,
        through_fields=("pinning", "status"),
    )
    priority: int = models.IntegerField(
        verbose_name="Приоритет",
        null=False,
        help_text="Чем меньше приоритет тем раньше проверяется условие",
    )
    result: str = models.CharField(
        verbose_name="Статус закрепления",
        choices=PinningStatusType.choices,
        max_length=36,
        null=False,
        help_text="Определяет статус закрепления конкретной сделки, соответствующий описанным выше условиям. "
                  "Проверяется при каждом изменении статуса сделки (и при ее создании). "
                  "Если хотя бы одна сделка клиента получает статус “Закреплен” (или аналогичный ему) - "
                  "проверка прекращается, в противном случае проверяются все сделки клиента",
    )
    assigned_to_agent: bool = models.BooleanField(
        verbose_name="Закреплен за проверяющим агентом",
        default=False,
    )
    assigned_to_another_agent: bool = models.BooleanField(
        verbose_name="Закреплен за другим агентом проверяющего агентства",
        default=False,
    )
    unique_status: models.ForeignKey = models.ForeignKey(
        verbose_name="Уникальный статус",
        to="disputes.UniqueStatus",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def _cities(self):
        return list(self.cities.values_list("name", flat=True))
    _cities.short_description = "Города"

    class Meta:
        managed = False
        db_table = "users_pinning_status"
        verbose_name = "Статус закрепления"
        verbose_name_plural = "6.1. Условия определения статуса закрепления"
        ordering = ["priority"]
