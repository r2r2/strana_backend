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
    city = models.ForeignKey(verbose_name="Город", to="cities.Cities", on_delete=models.CASCADE, unique=False)
    pinning = models.ForeignKey(to="users.PinningStatus", on_delete=models.CASCADE, related_name="city")

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
    pipeline = models.ForeignKey(verbose_name="Воронка", to="amocrm.AmocrmPipeline", on_delete=models.CASCADE, unique=False)
    pinning = models.ForeignKey(to="users.PinningStatus", on_delete=models.CASCADE, related_name="pipeline")

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
    status = models.ForeignKey(verbose_name="Статус", to="amocrm.AmocrmStatus", on_delete=models.CASCADE, unique=False)
    pinning = models.ForeignKey(to="users.PinningStatus", on_delete=models.CASCADE, related_name="status")

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
        to="cities.Cities",
        through="PinningStatusCity",
        blank=True,
        through_fields=("pinning", "city"),
    )
    pipelines = models.ManyToManyField(
        verbose_name="Воронки",
        to="amocrm.AmocrmPipeline",
        through="PinningStatusPipeline",
        blank=True,
        through_fields=("pinning", "pipeline"),
    )
    statuses = models.ManyToManyField(
        verbose_name="Статусы",
        to="amocrm.AmocrmStatus",
        through="PinningStatusStatus",
        blank=True,
        through_fields=("pinning", "status"),
    )
    priority: int = models.IntegerField(verbose_name="Приоритет", null=False)
    result: str = models.CharField(
        verbose_name="Статус закрепления",
        choices=PinningStatusType.choices,
        max_length=36,
        null=False,
    )

    def _cities(self):
        return list(self.cities.values_list("name", flat=True))
    _cities.short_description = "Города"

    class Meta:
        managed = False
        db_table = "users_pinning_status"
        verbose_name = "Статус закрепления"
        verbose_name_plural = "Статусы закрепления"
        ordering = ["priority"]
