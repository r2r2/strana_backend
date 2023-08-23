from django.db import models


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
    unique_status: models.ForeignKey = models.ForeignKey(
        verbose_name="Статус закрепления",
        to="disputes.UniqueStatus",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Определяет статус закрепления конкретной сделки, соответствующий описанным выше условиям. "
                  "Проверяется при каждом изменении статуса сделки (и при ее создании). "
                  "Если хотя бы одна сделка клиента получает статус “Закреплен” (или аналогичный ему) - "
                  "проверка прекращается, в противном случае проверяются все сделки клиента",
    )
    comment = models.TextField(
        verbose_name="Комментарий",
        null=True,
        blank=True,
        help_text="Внутренний комментарий по назначению статуса",
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
