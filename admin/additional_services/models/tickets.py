from django.db import models


class AdditionalServiceTicket(models.Model):
    """
    Заявка на доп услуги
    """

    service: models.ForeignKey = models.ForeignKey(
        to="additional_services.AdditionalService",
        related_name="service_ticket",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Услуга",
    )
    status: models.ForeignKey = models.ForeignKey(
        to="booking.AmocrmStatus",
        related_name="amocrm_status",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Статус заявки",
    )
    booking: models.ForeignKey = models.ForeignKey(
        to="booking.Booking",
        related_name="booking_ticket",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Сделка",
    )
    cost = models.DecimalField(
        decimal_places=2, max_digits=15, null=True, verbose_name="Стоимость"
    )
    full_name: str = models.CharField(max_length=150, verbose_name="ФИО клиента")
    phone: str = models.CharField(
        max_length=20, db_index=True, verbose_name="Номер телефона"
    )

    def __str__(self):
        return f"Заявка № {self.id}"

    class Meta:
        managed = False
        db_table = "additional_services_ticket"
        verbose_name = "заявка на услугу"
        verbose_name_plural = "17.1. [Доп. услуги] Заявка на услуги"
