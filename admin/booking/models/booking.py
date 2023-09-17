# pylint: disable=no-member
from datetime import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _
from pytz import UTC


class Booking(models.Model):
    __original_until = None
    __original_expires = None
    __original_payment_id = None
    __original_payment_amount = None
    __original_payment_url = None
    __original_payment_order_number = None
    __original_final_payment_amount = None
    __original_property = None
    __original_price_payed = False
    __original_contract_accepted = False
    __original_personal_filled = False
    __original_params_checked = False

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
    send_notify = models.BooleanField()
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
    fixation_expires = models.DateTimeField(verbose_name="Фиксация истекает", blank=True, null=True)
    origin = models.CharField(
        max_length=100, blank=True, null=True, help_text="Домен сайта, с которого пришла сделка"
    )
    tags = models.JSONField(blank=True, null=True, help_text="Теги сделки в АМО")
    online_purchase_id = models.CharField(max_length=9, blank=True, null=True)
    ddu_upload_url_secret = models.CharField(max_length=60, blank=True, null=True)
    signing_date = models.DateField(null=True, blank=True)
    created_source = models.CharField(choices=CreatedSourceChoices.choices, default=None, null=True,
                                      max_length=100, blank=True, help_text="Deprecated")
    booking_source = models.ForeignKey(
        to="BookingSource",
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name="bookings",
        verbose_name="Источник бронирования"
    )
    amocrm_status_id = models.IntegerField(null=True, blank=True)
    amocrm_status_name = models.CharField(null=True, blank=True, max_length=200)
    extension_number = models.IntegerField(
        verbose_name="Оставшиеся количество попыток продления",
        null=True,
        blank=True,
    )
    payment_method = models.ForeignKey(
        "booking.PaymentMethod",
        on_delete=models.SET_NULL,
        null=True,
        related_name="booking_payment_method",
        verbose_name="Способ оплаты",
        help_text="Способ оплаты",
    )
    price = models.ForeignKey(
        "properties.PropertyPrice",
        on_delete=models.SET_NULL,
        null=True,
        related_name="booking_price",
        verbose_name="Цена",
    )

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_until = self.until
        self.__original_expires = self.expires
        self.__original_payment_id = self.payment_id
        self.__original_payment_amount = self.payment_amount
        self.__original_payment_url = self.payment_url
        self.__original_payment_order_number = self.payment_order_number
        self.__original_final_payment_amount = self.final_payment_amount
        self.__original_property = self.property
        self.__original_fixation_expires = self.fixation_expires
        self.__original_extension_number = self.extension_number
        self.__original_project = self.project
        self.__original_contract_accepted = self.contract_accepted
        self.__original_personal_filled = self.personal_filled
        self.__original_params_checked = self.params_checked
        self.__original_price_payed = self.price_payed

    def save(self, *args, **kwargs):
        if self.__original_until and not self.until:
            self.until = self.__original_until
        if self.__original_expires and not self.expires:
            self.expires = self.__original_expires
        if self.__original_payment_id and not self.payment_id:
            self.payment_id = self.__original_payment_id
        if self.__original_payment_amount and not self.payment_amount:
            self.payment_amount = self.__original_payment_amount
        if self.__original_payment_url and not self.payment_url:
            self.payment_url = self.__original_payment_url
        if self.__original_payment_order_number and not self.payment_order_number:
            self.payment_order_number = self.__original_payment_order_number
        if self.__original_final_payment_amount and not self.final_payment_amount:
            self.final_payment_amount = self.__original_final_payment_amount
        if self.__original_property and not self.property:
            self.property = self.__original_property
        if self.__original_fixation_expires and not self.fixation_expires:
            self.fixation_expires = self.__original_fixation_expires
        if self.__original_extension_number and not self.extension_number:
            self.extension_number = self.__original_extension_number
        if self.__original_project and not self.project:
            self.project = self.__original_project
        if self.__original_contract_accepted and not self.contract_accepted:
            self.contract_accepted = self.__original_contract_accepted
        if self.__original_personal_filled and not self.personal_filled:
            self.personal_filled = self.__original_personal_filled
        if self.__original_params_checked and not self.params_checked:
            self.params_checked = self.__original_params_checked
        if self.__original_price_payed and not self.price_payed:
            self.price_payed = self.__original_price_payed

        super().save()
        self.__original_until = self.until
        self.__original_expires = self.expires
        self.__original_payment_id = self.payment_id
        self.__original_payment_amount = self.payment_amount
        self.__original_payment_url = self.payment_url
        self.__original_payment_order_number = self.payment_order_number
        self.__original_final_payment_amount = self.final_payment_amount
        self.__original_property = self.property
        self.__original_contract_accepted = self.contract_accepted
        self.__original_personal_filled = self.personal_filled
        self.__original_params_checked = self.params_checked
        self.__original_price_payed = self.price_payed

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
        verbose_name_plural = " 1.1. Бронирования (сделки)"
        ordering = ['-id']
