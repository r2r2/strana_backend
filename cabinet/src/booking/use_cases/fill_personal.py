from typing import Any, Callable, NamedTuple, Optional, Type, Union

from common.amocrm.types import AmoLead
from src.buildings.repos import BuildingBookingType, BuildingBookingTypeRepo
from ..constants import BookingStages, BookingSubstages, PaymentStatuses
from ..entities import BaseBookingCase
from ..loggers.wrappers import booking_changes_logger
from ..mixins import BookingLogMixin
from ..repos import Booking, BookingRepo
from ..types import BookingAmoCRM, BookingProfitBase
from ..models import RequestFillPersonalModel
from ..exceptions import (
    BookingNotFoundError,
    BookingPropertyUnavailableError,
    BookingTimeOutError,
    BookingWrongStepError
)


class BookingTypeNamedTuple(NamedTuple):
    price: int
    amocrm_id: Optional[int] = None


class FillPersonalCase(BaseBookingCase, BookingLogMixin):
    """
    Кейс заполнения персональных данных
    """
    lk_client_tag: list[str] = ["ЛК Клиента"]

    def __init__(
        self,
        create_amocrm_log_task: Any,
        booking_repo: Type[BookingRepo],
        amocrm_class: Type[BookingAmoCRM],
        profitbase_class: Type[BookingProfitBase],
        global_id_decoder: Callable[[str], tuple[str, Union[str, int]]],
        building_booking_type_repo: Type[BuildingBookingTypeRepo],
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.building_booking_type_repo: BuildingBookingTypeRepo = building_booking_type_repo()

        self.amocrm_class: Type[BookingAmoCRM] = amocrm_class
        self.create_amocrm_log_task: Any = create_amocrm_log_task
        self.profitbase_class: Type[BookingProfitBase] = profitbase_class
        self.global_id_decoder: Callable[[str], tuple[str, Union[str, int]]] = global_id_decoder
        self.booking_update: Callable = booking_changes_logger(
            self.booking_repo.update, self, content="Обновление бронирования",
        )
        self.booking_update_from_amo: Callable = booking_changes_logger(
            self.booking_repo.update, self, content="Забронировано | AMOCRM"
        )
        self.booking_update_from_profitbase: Callable = booking_changes_logger(
            self.booking_repo.update, self, content="Забронировано | PROFITBASE"
        )
        self.booking_fill_personal_data: Callable = booking_changes_logger(
            self.booking_repo.update, self, content="Заполнение персональных данных"
        )

    async def __call__(self, booking_id: int, user_id: int, payload: RequestFillPersonalModel) -> Booking:
        personal_filled_data: dict[str, Any] = dict(
            personal_filled=payload.personal_filled, email_force=payload.email_force
        )
        filters: dict[str, Any] = dict(id=booking_id, active=True, user_id=user_id)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters, related_fields=["user", "project", "property", "building"]
        )
        if not booking:
            raise BookingNotFoundError

        if booking.is_agent_assigned():
            booking: Booking = await self.booking_fill_personal_data(booking=booking, data=personal_filled_data)
            filters: dict[str, Any] = dict(active=True, id=booking.id, user_id=user_id)
            booking: Booking = await self.booking_repo.retrieve(
                filters=filters,
                related_fields=["project", "property", "floor", "building", "ddu", "agent", "agency"],
                prefetch_fields=["ddu__participants"],
            )
            return booking

        if not booking.step_one():
            raise BookingWrongStepError
        if booking.step_two():
            raise BookingWrongStepError
        if not booking.time_valid():
            raise BookingTimeOutError

        data: dict[str, Any] = dict(
            tags=["Онлайн-бронирование"],
            amocrm_stage=BookingStages.BOOKING,
            payment_status=PaymentStatuses.CREATED,
            amocrm_substage=BookingSubstages.BOOKING,
        )
        booking: Booking = await self.booking_update(booking=booking, data=data)

        lead_id: int = await self._amocrm_booking(booking=booking)
        data: dict[str, Any] = dict(amocrm_id=lead_id)
        booking: Booking = await self.booking_update_from_amo(booking=booking, data=data)

        profitbase_booked: bool = await self._profitbase_booking(booking=booking)
        data: dict[str, Any] = dict(profitbase_booked=profitbase_booked)
        booking: Booking = await self.booking_update_from_profitbase(booking=booking, data=data)
        booking: Booking = await self.booking_fill_personal_data(booking=booking, data=personal_filled_data)

        filters: dict[str, Any] = dict(active=True, id=booking.id, user_id=user_id)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters,
            related_fields=["project", "property", "floor", "building", "ddu", "agent", "agency"],
            prefetch_fields=["ddu__participants"],
        )
        return booking

    async def _amocrm_booking(self, booking: Booking) -> int:
        """
        Бронирование в AmoCRM
        """
        booking_type_filter = dict(period=booking.booking_period, price=booking.payment_amount)
        booking_type: Union[BuildingBookingType,
                            BookingTypeNamedTuple] = await self.building_booking_type_repo.retrieve(
            filters=booking_type_filter)
        if not booking_type:
            booking_type = BookingTypeNamedTuple(price=int(booking.payment_amount))

        async with await self.amocrm_class() as amocrm:
            lead_options: dict[str, Any] = dict(
                tags=booking.tags + self.lk_client_tag,
                status=BookingSubstages.START,
                city_slug=booking.project.city,
                property_id=self.global_id_decoder(booking.property.global_id)[1],
                property_type=booking.property.type.value.lower(),
                user_amocrm_id=booking.user.amocrm_id,
                booking_type_id=booking_type.amocrm_id,
                project_amocrm_name=booking.project.amocrm_name,
                project_amocrm_enum=booking.project.amocrm_enum,
                project_amocrm_pipeline_id=booking.project.amo_pipeline_id,
                project_amocrm_organization=booking.project.amocrm_organization,
                project_amocrm_responsible_user_id=booking.project.amo_responsible_user_id,
            )

            data: list[AmoLead] = await amocrm.create_lead(creator_user_id=booking.user.id, **lead_options)
            lead_id: int = data[0].id
            note_data: dict[str, Any] = dict(
                element="lead",
                lead_id=lead_id,
                note="lead_created",
                text="Создано онлайн-бронирование",
            )
            self.create_amocrm_log_task.delay(note_data=note_data)
            lead_options: dict[str, Any] = dict(
                status=BookingSubstages.BOOKING, lead_id=lead_id, city_slug=booking.project.city
            )
            data: list[Any] = await amocrm.update_lead(**lead_options)
            lead_id: int = data[0]["id"]
            note_data: dict[str, Any] = dict(
                element="lead",
                lead_id=lead_id,
                note="lead_changed",
                text="Изменен статус заявки на 'Бронь'",
            )
            self.create_amocrm_log_task.delay(note_data=note_data)
        return lead_id

    async def _profitbase_booking(self, booking: Booking) -> bool:
        """
        Бронированиве в profitbase
        """
        property_id: int = self.global_id_decoder(global_id=booking.property.global_id)[1]
        async with await self.profitbase_class() as profitbase:
            data: dict[str, bool] = await profitbase.book_property(
                property_id=property_id, deal_id=booking.amocrm_id
            )
            booked: bool = data.get("success", False)
            in_deal: bool = data.get("code", None) == profitbase.dealed_code
        profitbase_booked: bool = booked or in_deal
        if not profitbase_booked:
            raise BookingPropertyUnavailableError(booked, in_deal)
        return profitbase_booked
