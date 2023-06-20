"""
Booking repo
"""

from collections import OrderedDict
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Union, Any
from uuid import UUID, uuid4

from common import cfields, orm
from common.orm.mixins import CRUDMixin, FacetsMixin, SCountMixin, SpecsMixin
from pytz import UTC
from src.agencies.repos import Agency
from src.buildings.repos import Building
from src.floors.repos import Floor
from src.projects.repos import Project
from src.properties.repos import Property
from src.users.repos import User
from tortoise import Model, fields
from tortoise.queryset import QuerySet
from tortoise.fields import (ForeignKeyNullableRelation,
                             OneToOneNullableRelation)

from ..constants import (BookingCreatedSources, BookingStages,
                         BookingSubstages, OnlinePurchaseStatuses,
                         OnlinePurchaseSteps, PaymentMethods, PaymentStatuses,
                         PaymentView)
from ..entities import BaseBookingRepo
from ..types import ScannedPassportData
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
    origin: Optional[str] = fields.CharField(description="Сайт запроса", max_length=100, null=True)
    active: bool = fields.BooleanField(description="Активно", default=True)
    tags: Union[list, dict] = fields.JSONField(description="Тэги", null=True)
    until: Optional[datetime] = fields.DatetimeField(description="Забронировано до", null=True)
    booking_period: Optional[int] = fields.IntField(
        description="Длительность бронирования (дни)", null=True
    )
    created: Optional[datetime] = fields.DatetimeField(
        description="Создано", auto_now_add=True, null=True
    )
    expires: Optional[datetime] = fields.DatetimeField(description="Истекает", null=True)
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
    price_payed: bool = fields.BooleanField(description="Стоиомсть оплачена (шаг 4)", default=False)
    online_purchase_started: bool = fields.BooleanField(
        description="Клиент приступил к онлайн-покупке", default=False
    )
    payment_method_selected: bool = fields.BooleanField(
        description="Клиент указал способ покупки", default=False
    )
    amocrm_agent_data_validated: bool = fields.BooleanField(
        description="Данные были проверены агентом", default=False
    )
    ddu_created: bool = fields.BooleanField(description="ДДУ оформлен клиентом", default=False)
    amocrm_ddu_uploaded_by_lawyer: bool = fields.BooleanField(
        description="ДДУ был загружен юристом", default=False
    )
    ddu_accepted: bool = fields.BooleanField(description="Клиент согласовал ДДУ", default=False)
    escrow_uploaded: bool = fields.BooleanField(
        description="Клиент загрузил эскроу-счёт", default=False
    )
    amocrm_signing_date_set: bool = fields.BooleanField(
        description="Дата подписания договора была назначена", default=False
    )
    amocrm_signed: bool = fields.BooleanField(description="Договор был подписан", default=False)

    profitbase_booked: bool = fields.BooleanField(description="Забронировано в ПБ", default=False)

    email_sent: bool = fields.BooleanField(description="Отправлено на почту", default=False)
    email_force: bool = fields.BooleanField(description="Отправка без подтверждения", default=False)

    payment_id: Optional[UUID] = fields.UUIDField(description="ID платежа", null=True)
    payment_currency: int = fields.IntField(description="Валюта платежа", default=643)
    payment_order_number: UUID = fields.UUIDField(description="Номер заказа платежа", default=uuid4)
    payment_amount: Optional[Decimal] = fields.DecimalField(
        description="Стоимость платежа", decimal_places=2, max_digits=15, null=True
    )
    final_payment_amount: Optional[Decimal] = fields.DecimalField(
        description="Итоговая стоимость платежа", decimal_places=2, max_digits=15, null=True
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

    payment_method: str = cfields.CharChoiceField(
        description="Способ покупки",
        max_length=20,
        choice_class=PaymentMethods,
        null=True,
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

    amocrm_id: Optional[int] = fields.BigIntField(description="ID в AmoCRM", null=True, unique=True)

    # При разработке столкнулись с тем, что бронирований не было в AmoCRM, но были у нас.
    # То ли их там удалили, то ли ещё что произошло.
    # Крч, для синхронизации необходимо, чтобы не возникало ошибок,
    # связанных с тем, что у нас забронировано, а в profitbase и бэкенде - нет.
    deleted_in_amo: bool = fields.BooleanField(description="Удалено в AmoCRM", default=False)

    amocrm_stage: Optional[str] = cfields.CharChoiceField(
        description="Этап", max_length=100, null=True, choice_class=BookingStages
    )
    amocrm_substage: Optional[str] = cfields.CharChoiceField(
        description="Подэтап", max_length=100, null=True, choice_class=BookingSubstages
    )

    amocrm_status: ForeignKeyNullableRelation["AmocrmStatus"] = fields.ForeignKeyField(
         null=True, description="ID статуса из амо", model_name="models.AmocrmStatus", related_name="bookings"
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
    decremented: bool = fields.BooleanField(description="Комиссия снижена", default=False)
    decrement_reason: Optional[str] = fields.CharField(
        description="Причина снижения", max_length=300, null=True
    )

    floor: ForeignKeyNullableRelation[Floor] = fields.ForeignKeyField(
        description="Этаж", model_name="models.Floor", related_name="bookings", null=True
    )
    user: ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        description="Пользователь", model_name="models.User", related_name="bookings", null=True
    )
    agent: ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        description="Агент", model_name="models.User", related_name="reservations", null=True
    )
    agency: ForeignKeyNullableRelation[Agency] = fields.ForeignKeyField(
        description="Агентство", model_name="models.Agency", related_name="bookings", null=True
    )
    project: ForeignKeyNullableRelation[Project] = fields.ForeignKeyField(
        description="Проект", model_name="models.Project", related_name="bookings", null=True
    )
    building: ForeignKeyNullableRelation[Building] = fields.ForeignKeyField(
        description="Корпус", model_name="models.Building", related_name="bookings", null=True
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
    created_source: bool = cfields.CharChoiceField(
        description="Источник создания онлайн-бронирования",
        null=True,
        max_length=100,
        choice_class=BookingCreatedSources
    )

    task_instances: fields.ReverseRelation["TaskInstance"]
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

        if (
            self.amocrm_agent_data_validated
            or self.payment_method_selected
            and (
                self.payment_method in (PaymentMethods.CASH, PaymentMethods.INSTALLMENT_PLAN)
            )
        ):
            return OnlinePurchaseSteps.DDU_CREATE

        if self.payment_method_selected:
            return OnlinePurchaseSteps.AMOCRM_AGENT_DATA_VALIDATION

        if self.online_purchase_started:
            return OnlinePurchaseSteps.PAYMENT_METHOD_SELECT

        return OnlinePurchaseSteps.ONLINE_PURCHASE_START

    def time_valid(self) -> bool:
        return self.expires > datetime.now(tz=UTC)

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
            "amocrm_status"
        )


class BookingRepo(BaseBookingRepo, CRUDMixin, SCountMixin, FacetsMixin, SpecsMixin):
    """
    Репозиторий бронирования
    """

    non_false_fields = (
        "price_payed",
    )

    model = Booking
    q_builder: orm.QBuilder = orm.QBuilder(Booking)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(Booking)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(Booking)

    async def update_or_create(
        self,
        filters: dict[str, Any],
        data: dict[str, Any],
    ) -> 'UpdateOrCreateMixin.model':
        """
        Создание или обновление модели
        """
        data = {
            k: v for k, v in data.items()
            if (k in self.non_false_fields and v is not False) or k not in self.non_false_fields
        }

        model, _ = await self.model.update_or_create(**filters, defaults=data)
        return model

    async def update(self, model: Booking, data: dict[str, Any]) -> Booking:
        """
        Обновление модели
        """
        for field, value in data.items():
            if field in self.non_false_fields and value is False:
                continue
            setattr(model, field, value)
        await model.save()
        await model.refresh_from_db()
        return model

    async def bulk_update(
        self,
        data: dict[str, Any],
        filters: dict[str, Any],
        exclude_filters: dict[str, Any] = None,
    ) -> None:
        """
        Обновление пачки бронирований
        """

        data = {
            k: v for k, v in data.items()
            if (k in self.non_false_fields and v is not False) or k not in self.non_false_fields
        }

        if not exclude_filters:
            qs: QuerySet[Model] = self.model.select_for_update().filter(**filters)
        else:
            qs: QuerySet[Model] = self.model.select_for_update().filter(**filters).exclude(**exclude_filters)
        await qs.update(**data)
