from django.db import models


class Ticket(models.Model):
    """
    Заявка
    """
    name: str = models.CharField(max_length=255, verbose_name='Название')
    phone: str = models.CharField(max_length=20, verbose_name='Номер телефона')
    user_amocrm_id: int = models.IntegerField(
        verbose_name='ID пользователя в AmoCRM',
        null=True,
        blank=True,
    )
    booking_amocrm_id: int = models.IntegerField(
        verbose_name='ID брони в AmoCRM',
        null=True,
        blank=True,
    )
    note: str = models.TextField(
        verbose_name='Примечание',
        null=True,
        blank=True,
    )
    type: str = models.CharField(max_length=255, verbose_name='Тип')
    city: models.ManyToManyField = models.ManyToManyField(
        to="references.Cities",
        verbose_name='Город',
        related_name='tickets',
        help_text='Город',
        through='TicketCityThrough',
        through_fields=('ticket', 'city'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано',
        help_text='Время создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлено',
        help_text='Время последнего обновления'
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        managed = False
        db_table = 'dashboard_ticket'
        verbose_name = 'Заявка'
        verbose_name_plural = '12.2. Заявки'


class TicketCityThrough(models.Model):
    """
    Связь заявки и города
    """
    ticket: models.ForeignKey = models.ForeignKey(
        to='dashboard.Ticket',
        verbose_name='Заявка',
        related_name='ticket_through',
        on_delete=models.CASCADE,
        primary_key=True,
    )
    city: models.ForeignKey = models.ForeignKey(
        to='references.Cities',
        verbose_name='Город',
        related_name='city_through',
        on_delete=models.CASCADE,
    )

    class Meta:
        managed = False
        db_table = 'dashboard_ticket_city_through'
        verbose_name = 'Связь заявки и города'
        verbose_name_plural = 'Связи заявок и городов'

