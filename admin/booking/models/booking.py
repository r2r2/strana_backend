# pylint: disable=no-member
from datetime import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _
from pytz import UTC


class Booking(models.Model):
    class CreatedSourceChoices(models.TextChoices):
        AMOCRM = "amocrm", _("AMOCRM")
        LK = "lk_booking", _("Бронирование через личный кабинет")
        FAST_BOOKING = "fast_booking", _("Быстрое бронирование")
        LK_ASSIGN = "lk_booking_assign", _("Закреплен в ЛК Брокера")

    until = models.DateTimeField(blank=True, null=True, help_text="Дата окончания бронирования")
    created = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField()
    contract_accepted = models.BooleanField()
    personal_filled = models.BooleanField()
    params_checked = models.BooleanField()
    price_payed = models.BooleanField()
    online_purchase_started = models.BooleanField()
    payment_method_selected = models.BooleanField()
    amocrm_agent_data_validated = models.BooleanField()
    ddu_created = models.BooleanField()
    amocrm_ddu_uploaded_by_lawyer = models.BooleanField()
    ddu_accepted = models.BooleanField()
    escrow_uploaded = models.BooleanField()
    amocrm_signing_date_set = models.BooleanField()
    amocrm_signed = models.BooleanField()
    bill_paid = models.BooleanField()
    email_sent = models.BooleanField()
    email_force = models.BooleanField()
    should_be_deactivated_by_timer = models.BooleanField()
    payment_url = models.CharField(max_length=350, blank=True, null=True, help_text="Ссылка на оплату в эквайринге")
    amocrm_id = models.BigIntegerField(blank=True, null=True)
    amocrm_stage = models.CharField(max_length=100, blank=True, null=True)
    amocrm_substage = models.CharField(max_length=100, blank=True, null=True)
    project = models.ForeignKey("properties.Project", models.CASCADE, blank=True, null=True, verbose_name="ЖК")
    building = models.ForeignKey(
        "properties.Building", models.CASCADE, blank=True, null=True, verbose_name="Корпус"
    )
    user = models.ForeignKey(
        "users.CabinetUser",
        models.CASCADE,
        blank=True, null=True,
        related_name="booking_user",
        verbose_name="Клиент"
    )
    agent = models.ForeignKey(
        "users.CabinetUser",
        models.CASCADE,
        blank=True, null=True,
        related_name="booking_agent",
        verbose_name="Агент"
    )
    agency = models.ForeignKey(
        "users.Agency",
        models.DO_NOTHING,
        blank=True, null=True,
        related_name="booking_agency",
        verbose_name="Агентство"
    )
    property = models.ForeignKey(
        "properties.Property", models.CASCADE, blank=True, null=True, verbose_name="Объект недвижимости"
    )
    payment_order_number = models.UUIDField(help_text="Номер заказа в эквайринге")
    payment_currency = models.IntegerField(help_text="ID используемой валюты (643 - рубли)")
    payment_amount = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, help_text="Сумма оплаты без скидок"
    )
    final_payment_amount = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, help_text="Сумма оплаты с учетом скидок"
    )
    payment_id = models.UUIDField(blank=True, null=True, help_text="ID оплаты в эквайринге")
    payment_page_view = models.CharField(
        max_length=50,
        help_text="Тип устройства, с которого была проведена оплата. DESKTOP - полноразмерное устройство, "
                     "MOBILE - мобильное устройство",
    )
    payment_status = models.IntegerField(blank=True, null=True, help_text="Статус оплаты в эквайринге")
    floor = models.ForeignKey("properties.Floor", models.CASCADE, blank=True, null=True)
    profitbase_booked = models.BooleanField(help_text="Забронировано в Profitbase")
    expires = models.DateTimeField(blank=True, null=True)
    origin = models.CharField(
        max_length=100, blank=True, null=True, help_text="Домен сайта, с которого пришла сделка"
    )
    tags = models.JSONField(blank=True, null=True, help_text="Теги сделки в АМО")
    online_purchase_id = models.CharField(max_length=9, blank=True, null=True, help_text="Теги сделки в АМО")
    ddu_upload_url_secret = models.CharField(max_length=60, blank=True, null=True)
    signing_date = models.DateField(null=True, blank=True)
    created_source = models.CharField(choices=CreatedSourceChoices.choices, default=None, null=True,
                                      max_length=100, blank=True)
    amocrm_status_id = models.IntegerField(null=True, blank=True)
    amocrm_status_name = models.CharField(null=True, blank=True, max_length=200)

    def __str__(self) -> str:
        return f"Бронирование #{self.id} (AMOCRMID {self.amocrm_id})"

    def errors(self):
        return self.bookinglog_set.filter(error_data__isnull=False).exists()

    def completed(self):
        return bool(
            self.price_payed
            and self.contract_accepted
            and self.personal_filled
            and self.params_checked
            and self.profitbase_booked
        )

    def expired(self):
        return self.expires < datetime.now(tz=UTC) if self.expires else True

    def overed(self):
        return self.until < datetime.now(tz=UTC) if self.until else True

    errors.short_description = "Есть ошибки"
    errors.boolean = True
    completed.short_description = "Завершено"
    completed.boolean = True
    expired.short_description = "Истекло"
    expired.boolean = True
    overed.short_description = "Закончилось"
    overed.boolean = True

    class Meta:
        managed = False
        db_table = "booking_booking"
        verbose_name = "Бронирование"
        verbose_name_plural = "1.1. Бронирования (сделки)"
        ordering = ['-id']
