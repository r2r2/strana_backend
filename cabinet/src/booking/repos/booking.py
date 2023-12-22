"""
Booking repo
"""

import asyncio
from collections import OrderedDict
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Union, Any, Iterable
from uuid import UUID, uuid4
import traceback
from pytz import UTC

import structlog
from tortoise import Model, fields
from tortoise.fields import ForeignKeyNullableRelation, OneToOneNullableRelation
from tortoise.backends.base.client import BaseDBAsyncClient
from tortoise.queryset import QuerySet

from common import cfields, orm
from common.email import EmailService
from common.orm.mixins import CRUDMixin, FacetsMixin, SCountMixin, SpecsMixin, CountMixin

from common.unleash.client import UnleashClient
from config import MaintenanceSettings
from config.feature_flags import FeatureFlags
from src.agencies.repos import Agency
from src.buildings.repos import Building
from src.floors.repos import Floor
from src.projects.repos import Project
from src.properties.repos import Property
from src.users.repos import User
from src.booking.types import ScannedPassportData

from ..constants import (
    BookingCreatedSources,
    BookingStages,
    BookingSubstages,
    OnlinePurchaseStatuses,
    OnlinePurchaseSteps,
    PaymentStatuses,
    PaymentView,
)
from ..entities import BaseBookingRepo
from .bank_contact_info import BankContactInfo
from .ddu import DDU


class Booking(Model):
    """
    Бронирование
    """

    views = PaymentView()
    stages = BookingStages()
    statuses = PaymentStatuses()
    substages = BookingSubstages()

    id: int = fields.IntField(description="ID", pk=True)
    origin: Optional[str] = fields.CharField(
        description="Сайт запроса", max_length=100, null=True
    )
    active: bool = fields.BooleanField(description="Активно", default=True)
    tags: Union[list, dict] = fields.JSONField(description="Тэги", null=True)
    until: Optional[datetime] = fields.DatetimeField(
        description="Забронировано до", null=True
    )
    booking_period: Optional[int] = fields.IntField(
        description="Длительность бронирования (дни)", null=True
    )
    created: Optional[datetime] = fields.DatetimeField(
        description="Создано", auto_now_add=True, null=True
    )
    expires: Optional[datetime] = fields.DatetimeField(
        description="Истекает", null=True
    )
    fixation_expires: Optional[datetime] = fields.DatetimeField(
        description="Фиксация истекает", null=True
    )
    should_be_deactivated_by_timer: bool = fields.BooleanField(
        description="Бронирование должно быть деактивировано по таймеру", default=False
    )

    contract_accepted: bool = fields.BooleanField(
        description="Договор принят (шаг 1)", default=False
    )
    personal_filled: bool = fields.BooleanField(
        description="Персональные данные заполнены (шаг 2)", default=False
    )
    params_checked: bool = fields.BooleanField(
        description="Параметры проверены (шаг 3)", default=False
    )
    amo_payment_method = fields.ForeignKeyField(
        model_name="models.PaymentMethod",
        on_delete=fields.SET_NULL,
        null=True,
        related_name="booking_payment_method",
        description="Способ оплаты",
    )

    price = fields.ForeignKeyField(
        model_name="models.PropertyPrice",
        on_delete=fields.SET_NULL,
        related_name="bookings",
        description="Цена",
        null=True,
    )
    mortgage_type = fields.ForeignKeyField(
        model_name="models.MortgageType",
        on_delete=fields.SET_NULL,
        related_name="bookings",
        description="Тип ипотеки",
        null=True,
    )
    price_offer = fields.ForeignKeyField(
        model_name="models.PriceOfferMatrix",
        on_delete=fields.SET_NULL,
        related_name="bookings",
        description="Матрица предложения цены",
        null=True,
    )
    price_payed: bool = fields.BooleanField(
        description="Стоимость оплачена (шаг 4)", default=False
    )
    online_purchase_started: bool = fields.BooleanField(
        description="Клиент приступил к онлайн-покупке", default=False
    )
    payment_method_selected: bool = fields.BooleanField(
        description="Клиент указал способ покупки", default=False
    )
    amocrm_agent_data_validated: bool = fields.BooleanField(
        description="Данные были проверены агентом", default=False
    )
    ddu_created: bool = fields.BooleanField(
        description="ДДУ оформлен клиентом", default=False
    )
    amocrm_ddu_uploaded_by_lawyer: bool = fields.BooleanField(
        description="ДДУ был загружен юристом", default=False
    )
    ddu_accepted: bool = fields.BooleanField(
        description="Клиент согласовал ДДУ", default=False
    )
    escrow_uploaded: bool = fields.BooleanField(
        description="Клиент загрузил эскроу-счёт", default=False
    )
    amocrm_signing_date_set: bool = fields.BooleanField(
        description="Дата подписания договора была назначена", default=False
    )
    amocrm_signed: bool = fields.BooleanField(
        description="Договор был подписан", default=False
    )

    profitbase_booked: bool = fields.BooleanField(
        description="Забронировано в ПБ", default=False
    )

    email_sent: bool = fields.BooleanField(
        description="Отправлено на почту", default=False
    )
    email_force: bool = fields.BooleanField(
        description="Отправка без подтверждения", default=False
    )

    payment_id: Optional[UUID] = fields.UUIDField(description="ID платежа", null=True)
    payment_currency: int = fields.IntField(description="Валюта платежа", default=643)
    payment_order_number: UUID = fields.UUIDField(
        description="Номер заказа платежа", default=uuid4
    )
    payment_amount: Optional[Decimal] = fields.DecimalField(
        description="Стоимость платежа", decimal_places=2, max_digits=15, null=True
    )
    final_payment_amount: Optional[Decimal] = fields.DecimalField(
        description="Итоговая стоимость платежа",
        decimal_places=2,
        max_digits=15,
        null=True,
    )
    final_discount: Optional[Decimal] = fields.DecimalField(
        description="Общий размер скидки", decimal_places=2, max_digits=15, null=True
    )
    final_additional_options: Optional[Decimal] = fields.DecimalField(
        description="Общая стоимость доп. опций",
        decimal_places=2,
        max_digits=15,
        null=True,
    )
    payment_url: Optional[str] = fields.CharField(
        description="Ссылка на оплату платежа", max_length=350, null=True
    )
    payment_status: Optional[int] = cfields.IntChoiceField(
        description="Статус платежа", null=True, choice_class=PaymentStatuses
    )
    bill_paid: bool = fields.BooleanField(description="Счет оплачен", default=False)
    payment_page_view: str = cfields.CharChoiceField(
        description="Вид страницы платежа",
        max_length=50,
        default=PaymentView.DESKTOP,
        choice_class=PaymentView,
    )
    maternal_capital: bool = fields.BooleanField(
        description="Материнский капитал (способ покупки)", default=False
    )
    housing_certificate: bool = fields.BooleanField(
        description="Жилищный сертификат (способ покупки)", default=False
    )
    government_loan: bool = fields.BooleanField(
        description="Государственный займ (способ покупки)", default=False
    )

    amocrm_id: Optional[int] = fields.BigIntField(
        description="ID в AmoCRM", null=True, unique=True
    )

    # При разработке столкнулись с тем, что бронирований не было в AmoCRM, но были у нас.
    # То ли их там удалили, то ли ещё что произошло.
    # Крч, для синхронизации необходимо, чтобы не возникало ошибок,
    # связанных с тем, что у нас забронировано, а в profitbase и бэкенде - нет.
    deleted_in_amo: bool = fields.BooleanField(
        description="Удалено в AmoCRM", default=False
    )

    amocrm_stage: Optional[str] = cfields.CharChoiceField(
        description="Этап", max_length=100, null=True, choice_class=BookingStages
    )
    amocrm_substage: Optional[str] = cfields.CharChoiceField(
        description="Подэтап", max_length=100, null=True, choice_class=BookingSubstages
    )

    amocrm_status: ForeignKeyNullableRelation["AmocrmStatus"] = fields.ForeignKeyField(
        null=True,
        description="ID статуса из амо",
        model_name="models.AmocrmStatus",
        related_name="bookings",
    )

    amocrm_purchase_status: Optional[str] = cfields.CharChoiceField(
        description="Cтатус онлайн-покупки",
        max_length=100,
        null=True,
        choice_class=OnlinePurchaseStatuses,
    )

    start_commission: Optional[Decimal] = fields.DecimalField(
        description="Стартовая комиссия", decimal_places=2, max_digits=15, null=True
    )
    commission: Optional[Decimal] = fields.DecimalField(
        description="Комиссия", decimal_places=2, max_digits=15, null=True
    )
    commission_value: Optional[Decimal] = fields.DecimalField(
        description="Комиссия в рублях", decimal_places=2, max_digits=15, null=True
    )
    decremented: bool = fields.BooleanField(
        description="Комиссия снижена", default=False
    )
    decrement_reason: Optional[str] = fields.CharField(
        description="Причина снижения", max_length=300, null=True
    )

    floor: ForeignKeyNullableRelation[Floor] = fields.ForeignKeyField(
        description="Этаж",
        model_name="models.Floor",
        related_name="bookings",
        null=True,
    )
    user: ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        description="Пользователь",
        model_name="models.User",
        related_name="bookings",
        null=True,
    )
    agent: ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        description="Агент",
        model_name="models.User",
        related_name="reservations",
        null=True,
    )
    agency: ForeignKeyNullableRelation[Agency] = fields.ForeignKeyField(
        description="Агентство",
        model_name="models.Agency",
        related_name="bookings",
        null=True,
    )
    project: ForeignKeyNullableRelation[Project] = fields.ForeignKeyField(
        description="Проект",
        model_name="models.Project",
        related_name="bookings",
        null=True,
    )
    building: ForeignKeyNullableRelation[Building] = fields.ForeignKeyField(
        description="Корпус",
        model_name="models.Building",
        related_name="bookings",
        null=True,
    )
    property: ForeignKeyNullableRelation[Property] = fields.ForeignKeyField(
        description="Объект недвижимости",
        model_name="models.Property",
        related_name="bookings",
        null=True,
    )

    purchase_start_datetime: Optional[datetime] = fields.DatetimeField(
        description="Дата и время начала онлайн-покупки", null=True
    )
    client_has_an_approved_mortgage: Optional[bool] = fields.BooleanField(
        description="У клиента есть одобренная ипотека", null=True
    )
    bank_contact_info: OneToOneNullableRelation[BankContactInfo] = fields.OneToOneField(
        description="Данные для связи с банком",
        model_name="models.BankContactInfo",
        related_name="booking",
        null=True,
    )
    mortgage_request_selected: Optional[bool] = fields.BooleanField(
        description="Клиент хочет подать заявку на ипотеку", null=True
    )
    online_purchase_id: Optional[str] = fields.CharField(
        description="ID онлайн-покупки", max_length=9, unique=True, null=True
    )
    ddu: OneToOneNullableRelation[DDU] = fields.OneToOneField(
        description="ДДУ", model_name="models.DDU", related_name="booking", null=True
    )
    ddu_upload_url_secret: Optional[str] = fields.CharField(
        description="Секретная часть URL-а загрузки ДДУ", max_length=100, null=True
    )
    ddu_acceptance_datetime: Optional[datetime] = fields.DatetimeField(
        description="Дата и время согласования ДДУ клиентом", null=True
    )
    signing_date: Optional[date] = fields.DateField(
        description="День для подписания договора", null=True
    )
    files: Optional[Union[list, dict]] = cfields.MutableDocumentContainerField(
        description="Файлы", null=True
    )
    scanned_passports_data: list[ScannedPassportData] = fields.JSONField(
        description="Отсканированные данные паспортов", null=True
    )
    created_source: str = cfields.CharChoiceField(
        # todo: deprecated. New field is booking_source(ForeignKey)
        description="Источник создания онлайн-бронирования",
        null=True,
        max_length=100,
        choice_class=BookingCreatedSources,
    )
    booking_source: ForeignKeyNullableRelation["BookingSource"] = fields.ForeignKeyField(
        description="Источник создания онлайн-бронирования",
        model_name="models.BookingSource",
        related_name="bookings",
        null=True,
    )
    condition_chosen: bool = fields.BooleanField(
        description='На стадии "Выбор условий"', default=False
    )
    send_notify: bool = fields.BooleanField(
        description="Отправить уведомление", default=True
    )
    extension_number: int = fields.IntField(
        description="Оставшиеся количество попыток продления", null=True
    )
    pay_extension_number: int = fields.IntField(
        description="Количество продлений при неуспешной оплате", null=True
    )

    loyalty_point_amount: int | None = fields.IntField(
        description="Количество баллов лояльности", null=True
    )

    clients: fields.ManyToManyRelation["User"] = fields.ManyToManyField(
        model_name="models.User",
        related_name="booking_all_clients",
        through="booking_booking_client_user_through",
        description="Клиенты",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="booking_id",
        forward_key="client_id",
    )

    task_instances: fields.ReverseRelation["TaskInstance"]
    mortgage_dev_tickets: fields.ReverseRelation["MortgageDeveloperTicket"]
    mortgage_type_id: int | None
    property_id: Optional[int]
    project_id: Optional[int]
    agency_id: Optional[int]
    agent_id: Optional[int]
    user_id: Optional[int]

    def __str__(self) -> str:
        return str(self.id)

    def step_one(self) -> bool:
        return self.contract_accepted

    def step_two(self) -> bool:
        return self.step_one() and self.personal_filled

    def step_three(self) -> bool:
        return self.step_two() and self.params_checked

    def step_four(self) -> bool:
        return self.step_three() and self.price_payed

    def is_fast_booking(self) -> bool:
        return "Быстрая бронь" in self.tags if self.tags else False

    def is_agent_assigned(self) -> bool:
        return True if self.agent_id else False

    def is_agency_assigned(self) -> bool:
        return True if self.agency_id else False

    def is_condition_chosen(self) -> bool:
        """
        Сделка находится на шаге "Выбор условий"
        """
        return self.condition_chosen

    def current_step(self) -> int:
        """
        Текущий шаг сделки
        """
        current_step: Optional[int] = 4
        step_mapping: OrderedDict[str, int] = OrderedDict(
            [
                ("contract_accepted", 0),
                ("personal_filled", 1),
                ("params_checked", 2),
                ("price_payed", 3),
            ]
        )
        for step_name, step in step_mapping.items():
            if not getattr(self, step_name):
                current_step: int = step
                break

        if current_step < 3:
            current_step += 1

        return current_step

    def continue_link(self) -> str:
        return f"{self.origin}/booking/{self.id}/{self.current_step()}"

    def online_purchase_step(self) -> Optional[str]:
        """Текущий шаг онлайн-покупки."""
        if not self.price_payed:
            return None

        if self.amocrm_signed:
            return OnlinePurchaseSteps.FINISHED

        if self.amocrm_signing_date_set and self.escrow_uploaded:
            return OnlinePurchaseSteps.AMOCRM_SIGNING

        if self.escrow_uploaded:
            return OnlinePurchaseSteps.AMOCRM_SIGNING_DATE

        if self.ddu_accepted:
            return OnlinePurchaseSteps.ESCROW_UPLOAD

        if self.amocrm_ddu_uploaded_by_lawyer:
            return OnlinePurchaseSteps.DDU_ACCEPT

        if self.ddu_created:
            return OnlinePurchaseSteps.AMOCRM_DDU_UPLOADING_BY_LAWYER

        if self.payment_method_selected:
            return OnlinePurchaseSteps.AMOCRM_AGENT_DATA_VALIDATION

        if self.online_purchase_started:
            return OnlinePurchaseSteps.PAYMENT_METHOD_SELECT

        return OnlinePurchaseSteps.ONLINE_PURCHASE_START

    def time_valid(self) -> bool:
        return self.expires > datetime.now(tz=UTC)

    def is_can_pay(self) -> bool:
        if self.pay_extension_number is not None and self.pay_extension_number < 0:
            return False

        return True

    async def save(
        self,
        using_db: Optional[BaseDBAsyncClient] = None,
        update_fields: Optional[Iterable[str]] = None,
        force_create: bool = False,
        force_update: bool = False,
    ) -> None:
        if not force_create and (
            not self.until
            or not self.expires
            or not self.payment_id
            or not self.payment_amount
            or not self.payment_url
            or not self.payment_order_number
            or not self.final_payment_amount
            or not self.property_id
            or not self.property
            or not self.fixation_expires
            or not self.extension_number
            or not self.project_id
            or not self.loyalty_point_amount
            or not self.contract_accepted
            or not self.personal_filled
            or not self.params_checked
            or not self.price_payed
        ):
            booking: Booking = await BookingRepo().retrieve(filters=dict(id=self.id))
            ##########################################
            unleash_client = UnleashClient()
            is_strana_lk_2398_enable: bool = unleash_client.is_enabled(FeatureFlags.strana_lk_2398)
            if is_strana_lk_2398_enable:
                stack_trace: str = "".join(traceback.format_stack(limit=5))
                fields_to_check: tuple[str, ...] = (
                    "until",
                    "expires",
                    "payment_id",
                    "payment_amount",
                    "payment_url",
                    "payment_order_number",
                    "final_payment_amount",
                    "property_id",
                    "property",
                    "fixation_expires",
                    "extension_number",
                    "project_id",
                    "contract_accepted",
                    "personal_filled",
                    "params_checked",
                    "price_payed",
                )
                data: dict[str, Any] = {}
                for field in fields_to_check:
                    if getattr(self, field) != getattr(booking, field):
                        data.update({field: getattr(self, field)})

                await _send_email(
                    data=data,
                    model=booking,
                    topic='Booking save',
                    stack_trace=stack_trace,
                    fields_to_check=fields_to_check,
                )
            ##########################################
            if not self.until and booking.until:
                self.until = booking.until
            if not self.expires and booking.expires:
                self.expires = booking.expires
            if not self.payment_id and booking.payment_id:
                self.payment_id = booking.payment_id
            if not self.payment_amount and booking.payment_amount:
                self.payment_amount = booking.payment_amount
            if not self.payment_url and booking.payment_url:
                self.payment_url = booking.payment_url
            if not self.payment_order_number and booking.payment_order_number:
                self.payment_order_number = booking.payment_order_number
            if not self.final_payment_amount and booking.final_payment_amount:
                self.final_payment_amount = booking.final_payment_amount
            if not self.property_id and booking.property_id:
                self.property_id = booking.property_id
            if not self.property and booking.property:
                self.property = await booking.property
            if not self.fixation_expires and booking.fixation_expires:
                self.fixation_expires = booking.fixation_expires
            if not self.extension_number and booking.extension_number:
                self.extension_number = booking.extension_number
            if not self.project_id and booking.project_id:
                self.project_id = booking.project_id
            if not self.loyalty_point_amount and booking.loyalty_point_amount:
                self.loyalty_point_amount = booking.loyalty_point_amount
            if not self.contract_accepted and booking.contract_accepted:
                self.contract_accepted = booking.contract_accepted
            if not self.personal_filled and booking.personal_filled:
                self.personal_filled = booking.personal_filled
            if not self.params_checked and booking.params_checked:
                self.params_checked = booking.params_checked
            if not self.price_payed and booking.price_payed:
                self.price_payed = booking.price_payed
        await super().save(using_db, update_fields, force_create, force_update)

    class Meta:
        table = "booking_booking"

    class PydanticMeta:
        computed = ("online_purchase_step",)
        exclude = (
            "user",
            "floor",
            "agent",
            "agency",
            "project",
            "building",
            "property",
            "amocrm_stage",
            "booking_logs",
            "booking_tags",
            "payment_status",
            "amocrm_substage",
            "payment_page_view",
            "payment_method",
            "bank_contact_info",
            "mortgage_request",
            "ddu",
            "amocrm_purchase_status",
            "files",
            "created_source",
            "amocrm_status",
        )


class BookingClientsUserThrough(Model):
    """
    Все пользователи которые участвуют в сделке
    """

    booking: fields.ForeignKeyRelation[Booking] = fields.ForeignKeyField(
        model_name="models.Booking",
        related_name="user_through",
        description="Сделка",
        on_delete=fields.CASCADE,
    )
    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        model_name="models.User",
        related_name="booking_through",
        description="Клиент",
        on_delete=fields.CASCADE,
    )

    is_main: bool = fields.BooleanField(description="Главный клиент сделки", default=False)

    class Meta:
        table = "booking_booking_client_user_through"


class BookingRepo(BaseBookingRepo, CRUDMixin, SCountMixin, FacetsMixin, SpecsMixin, CountMixin):
    """
    Репозиторий бронирования
    """

    model = Booking
    q_builder: orm.QBuilder = orm.QBuilder(Booking)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(Booking)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(Booking)

    logger = structlog.get_logger("booking_repo")

    @property
    def non_nullable_fields(self) -> tuple[str, ...]:
        non_nullable_fields = (
            "until",
            "expires",
            "payment_id",
            "payment_amount",
            "payment_url",
            "payment_order_number",
            "final_payment_amount",
            "property_id",
            "property",
            "fixation_expires",
            "extension_number",
            "project_id",
            "loyalty_point_amount",
        )
        return non_nullable_fields

    @property
    def non_false_fields(self) -> tuple[str, ...]:
        non_false_fields = (
            "contract_accepted",
            "personal_filled",
            "params_checked",
            "price_payed",
        )
        return non_false_fields

    async def create(self, data: dict[str, Any]) -> "CreateMixin.model":
        model = await super().create(data)

        self.logger.debug("Booking create: ", id=model.id, data=data)
        self.logger.debug(traceback.print_stack(limit=5))

        return model

    async def update_or_create(
        self,
        filters: dict[str, Any],
        data: dict[str, Any],
    ) -> "UpdateOrCreateMixin.model":
        """
        Создание или обновление модели
        """
        if self.__is_strana_lk_2398_enable:
            if booking := await self.model.get_or_none(**filters):
                stack_trace: str = "".join(traceback.format_stack(limit=5))
                await _send_email(
                    data=data.copy(),
                    model=booking,
                    topic="Booking update_or_create",
                    stack_trace=stack_trace,
                    fields_to_check=self.non_false_fields + self.non_nullable_fields,
                )

        for non_nullable_field in self.non_nullable_fields:
            if non_nullable_field in data:
                if data.get(non_nullable_field) is None:
                    data.pop(non_nullable_field)

        for non_false_field in self.non_false_fields:
            if non_false_field in data:
                if data.get(non_false_field) is False:
                    data.pop(non_false_field)

        model, _ = await self.model.update_or_create(**filters, defaults=data)

        self.logger.debug("Booking update_or_create: ", id=model.id, data=data)
        self.logger.debug(traceback.print_stack(limit=5))

        return model

    async def update(self, model: Booking, data: dict[str, Any]) -> Booking:
        """
        Обновление модели
        """
        print("Booking data: ", data)
        self.logger.debug("Booking update: ", id=model.id, data=data)
        self.logger.debug(traceback.print_stack(limit=5))

        if self.__is_strana_lk_2398_enable:
            stack_trace: str = "".join(traceback.format_stack(limit=5))
            await _send_email(
                data=data,
                model=model,
                topic="Booking update",
                stack_trace=stack_trace,
                fields_to_check=self.non_false_fields + self.non_nullable_fields,
            )

        for field, value in data.items():
            if field in self.non_false_fields and value is False:
                continue
            elif field in self.non_nullable_fields and value is None:
                continue
            setattr(model, field, value)
        await model.save()
        await model.refresh_from_db()
        return model

    async def bulk_update(
        self,
        data: dict[str, Any],
        filters: dict[str, Any],
        exclude_filters: list[dict] = None,
    ) -> None:
        """
        Обновление пачки бронирований
        """
        self.logger.debug("Booking bulk_update: ", filters=filters, data=data)
        self.logger.debug(traceback.print_stack(limit=5))

        if self.__is_strana_lk_2398_enable:
            if bookings := await self.model.all(**filters):
                stack_trace: str = "".join(traceback.format_stack(limit=5))
                data_copy: dict[str, Any] = data.copy()
                for booking in bookings:
                    await _send_email(
                        data=data_copy,
                        model=booking,
                        topic="Booking bulk_update",
                        stack_trace=stack_trace,
                        fields_to_check=self.non_false_fields
                        + self.non_nullable_fields,
                    )

        for non_nullable_field in self.non_nullable_fields:
            if non_nullable_field in data:
                if data.get(non_nullable_field) is None:
                    data.pop(non_nullable_field)

        for non_false_field in self.non_false_fields:
            if non_false_field in data:
                if data.get(non_false_field) is False:
                    data.pop(non_false_field)

        qs: QuerySet[Model] = self.model.select_for_update().filter(**filters)
        if exclude_filters:
            for exclude_filter in exclude_filters:
                qs: QuerySet[Model] = qs.exclude(**exclude_filter)
        await qs.update(**data)

    @property
    def __is_strana_lk_2398_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_2398)


async def _send_email(
    data: dict[str, Any],
    model: Booking,
    topic: str,
    stack_trace: str,
    fields_to_check: tuple[str, ...] = None,
) -> asyncio.Task | None:
    send_email: bool = False
    for field in fields_to_check:
        if field in data and data[field] is None and getattr(model, field) is not None:
            send_email: bool = True
            break

    if not send_email:
        return

    topic += f" [{MaintenanceSettings().environment.value}]"
    context = dict(
        booking=model.id,
        data=data,
        stack_trace=stack_trace,
    )
    recipients: list[str] = ["krasnykh@artw.ru"]
    email_options: dict[str, Any] = dict(
        topic=topic,
        context=context,
        recipients=recipients,
        template="src/booking/templates/booking_logs/booking_update.html",
    )
    email_service: EmailService = EmailService(**email_options)
    return email_service.as_task()
