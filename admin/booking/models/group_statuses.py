from django.db import models


class AmocrmGroupStatus(models.Model):
    """
    Таблица группирующих статусов из AmoCRM
    """

    sort = models.IntegerField(verbose_name='Сортировка', default=0)
    name = models.CharField(verbose_name='Название статуса', max_length=150)
    color = models.CharField(verbose_name='Цвет', max_length=40, blank=True, null=True)
    is_final = models.BooleanField(verbose_name='Завершающий статус', default=False)

    # Deprecated
    show_reservation_date: bool = models.BooleanField(verbose_name="Выводить дату резерва", default=False)
    show_booking_date: bool = models.BooleanField(verbose_name="Выводить дату брони", default=False)

    actions = models.ManyToManyField(
        null=True, blank=True,
        verbose_name="Действия по сделкам",
        to="booking.AmocrmAction",
        through="GroupStatusActionThrough",
        through_fields=("group_status", "action"),
        related_name="actions",
    )

    tags = models.ManyToManyField(
        null=True, blank=True,
        verbose_name="Теги",
        to="booking.BookingTag",
        through="GroupStatusTagThrough",
        through_fields=("group_status", "tag"),
        related_name="tags",
    )

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "amocrm_group_statuses"
        ordering = ("sort",)
        verbose_name = "Группирующий статус"
        verbose_name_plural = "1.3. [Справочник] Группирующие статусы воронок"


class GroupStatusActionThrough(models.Model):
    group_status = models.ForeignKey(
        verbose_name="Статус",
        to="booking.AmocrmGroupStatus",
        on_delete=models.CASCADE,
        related_name="group_status",
        primary_key=True
    )
    action = models.ForeignKey(
        verbose_name="Действие",
        to="booking.AmocrmAction",
        on_delete=models.CASCADE,
        unique=False,
        related_name="action"
    )

    class Meta:
        managed = False
        db_table = "amocrm_actions_group_statuses"
        unique_together = ('group_status', 'action')
        verbose_name = "Групповой статус-Действие"
        verbose_name_plural = "Групповые статусы-Действия"

    def __str__(self):
        return f"{self.group_status} {self.action}"
