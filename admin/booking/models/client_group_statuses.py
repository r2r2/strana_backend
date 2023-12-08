from django.db import models


class ClientAmocrmGroupStatus(models.Model):
    """
    Таблица группирующих статусов из AmoCRM для клиентов
    """

    sort = models.IntegerField(verbose_name='Сортировка', default=0)
    name = models.CharField(verbose_name='Название статуса', max_length=150)
    color = models.CharField(verbose_name='Цвет', max_length=40, blank=True)
    is_final = models.BooleanField(verbose_name='Завершающий статус', default=False)

    # Deprecated
    show_reservation_date: bool = models.BooleanField(verbose_name="Выводить дату резерва", default=False)
    show_booking_date: bool = models.BooleanField(verbose_name="Выводить дату брони", default=False)

    tags = models.ManyToManyField(
        blank=True,
        verbose_name="Теги",
        to="booking.BookingTag",
        through="ClientGroupStatusTagThrough",
        through_fields=("client_group_status", "tag"),
        related_name="client_tags",
    )
    is_hide = models.BooleanField(
        verbose_name="Скрыть статус",
        help_text="Данный групповой статус будет скрыт в списке броней",
        default=False,
    )

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "client_amocrm_group_statuses"
        ordering = ("sort",)
        verbose_name = "Группирующий статус для клиента"
        verbose_name_plural = "1.10. [Справочник] Группирующие статусы ЛК клиента в списке броней"
