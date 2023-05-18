# pylint: disable=no-member
from datetime import datetime

from common.loggers.models import AbstractLog
from django.db import models
from django.utils.translation import gettext_lazy as _
from pytz import UTC


class Booking(models.Model):
    class CreatedSourceChoices(models.TextChoices):
        AMOCRM = "amocrm", _("AMOCRM")
        LK = "lk_booking", _("Бронирование через личный кабинет")
        FAST_BOOKING = "fast_booking", _("Быстрое бронирование")
        LK_ASSIGN = "lk_booking_assign", _("Закреплен в ЛК Брокера")

    until = models.DateTimeField(blank=True, null=True)
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
    payment_url = models.CharField(max_length=350, blank=True, null=True)
    amocrm_id = models.BigIntegerField(blank=True, null=True)
    amocrm_stage = models.CharField(max_length=100, blank=True, null=True)
    amocrm_substage = models.CharField(max_length=100, blank=True, null=True)
    project = models.ForeignKey("projects.Project", models.CASCADE, blank=True, null=True)
    building = models.ForeignKey("buildings.Building", models.CASCADE, blank=True, null=True)
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
        "agencies.Agency",
        models.DO_NOTHING,
        blank=True, null=True,
        related_name="booking_agency",
        verbose_name="Агентство"
    )
    property = models.ForeignKey("properties.Property", models.CASCADE, blank=True, null=True)
    payment_order_number = models.UUIDField()
    payment_currency = models.IntegerField()
    payment_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    final_payment_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    payment_id = models.UUIDField(blank=True, null=True)
    payment_page_view = models.CharField(max_length=50)
    payment_status = models.IntegerField(blank=True, null=True)
    floor = models.ForeignKey("floors.Floor", models.CASCADE, blank=True, null=True)
    profitbase_booked = models.BooleanField()
    expires = models.DateTimeField(blank=True, null=True)
    origin = models.CharField(max_length=100, blank=True, null=True)
    tags = models.JSONField(blank=True, null=True)
    online_purchase_id = models.CharField(max_length=9, blank=True, null=True)
    ddu_upload_url_secret = models.CharField(max_length=60, blank=True, null=True)
    signing_date = models.DateField(null=True, blank=True)
    created_source = models.CharField(choices=CreatedSourceChoices.choices, default=None, null=True,
                                      max_length=100, blank=True)
    amocrm_status_id = models.IntegerField(null=True, blank=True)
    amocrm_status_name = models.CharField(null=True, blank=True, max_length=200)

    def __str__(self) -> str:
        return f"Бронирование #{self.id}"

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
        verbose_name_plural = "Бронирования"
        ordering = ['-id']


class BookingLog(AbstractLog):
    booking = models.ForeignKey("booking.Booking", models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.use_case} – {self.content}" if self.use_case and self.content else self

    class Meta:
        db_table = "booking_bookinglog"
        verbose_name = "Лог: "
        verbose_name_plural = "Логи бронирований"


class BookingHelpText(models.Model):
    class OnlinePurchaseSteps(models.TextChoices):
        ONLINE_PURCHASE_START = "online_purchase_start", "Начало онлайн покупки"
        PAYMENT_METHOD_SELECT = "payment_method_select", "Выбор способа покупки"
        AMOCRM_AGENT_DATA_VALIDATION = (
            "amocrm_agent_data_validation",
            "Ожидайте, введённые данные на проверке",
        )
        DDU_CREATE = "ddu_create", "Оформление договора"
        AMOCRM_DDU_UPLOADING_BY_LAWYER = (
            "amocrm_ddu_uploading_by_lawyer",
            "Ожидание загрузки ДДУ юристом",
        )
        DDU_ACCEPT = "ddu_accept", "Согласование договора"
        ESCROW_UPLOAD = "escrow_upload", "Загрузка эскроу-счёта"
        AMOCRM_SIGNING_DATE = (
            "amocrm_signing_date",
            "Ожидание назначения даты подписания договора",
        )
        AMOCRM_SIGNING = "amocrm_signing", "Ожидание подписания договора"
        FINISHED = "finished", "Зарегистрировано"

    class PaymentMethods(models.TextChoices):
        CASH = "cash", "Наличные"
        MORTGAGE = "mortgage", "Ипотека"
        INSTALLMENT_PLAN = "installment_plan", "Рассрочка"

    text = models.TextField(verbose_name="Текст")
    booking_online_purchase_step = models.CharField(
        verbose_name="Стадия онлайн-покупки", max_length=50, choices=OnlinePurchaseSteps.choices
    )
    payment_method = models.CharField(
        verbose_name="Тип покупки", max_length=20, choices=PaymentMethods.choices
    )
    maternal_capital = models.BooleanField(verbose_name="Мат. капитал")
    certificate = models.BooleanField(verbose_name="Жил. сертификат")
    loan = models.BooleanField(verbose_name="Гос. займ")
    default = models.BooleanField(verbose_name="Текст по-умолчанию", default=False)

    class Meta:
        managed = False
        db_table = "booking_purchase_help_text"
        verbose_name = 'Текст для страницы "Как купить онлайн?"'
        verbose_name_plural = 'Тексты для страницы "Как купить онлайн?"'
        ordering = [
            "default",
            "booking_online_purchase_step",
            "payment_method",
            "id",
        ]
