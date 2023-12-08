from typing import Any

from src.amocrm.repos import AmocrmGroupStatus, AmocrmGroupStatusRepo
from src.buildings.repos import BuildingBookingType, BuildingBookingTypeRepo
from src.payments import repos as payment_repos
from src.task_management.constants import (
    FastBookingSlug,
    FreeBookingSlug,
    OnlineBookingSlug,
)
from src.task_management.repos import TaskStatus
from src.task_management.utils import (
    get_interesting_task_chain,
    get_booking_tasks,
)

from ..constants import BookingCreatedSources
from ..entities import BaseBookingCase
from ..exceptions import (
    BookingNotFoundError,
    BookingTimeOutError,
    BookingTimeOutRepeatError,
)
from ..repos import Booking, BookingRepo, BookingTag, BookingTagRepo
from ..types import BookingSession


class BookingRetrieveCase(BaseBookingCase):
    """
    Детальное бронирование
    """

    def __init__(
        self,
        session: BookingSession,
        session_config: dict,
        booking_repo: type[BookingRepo],
        booking_tag_repo: type[BookingTagRepo],
        booking_type_repo: type[BuildingBookingTypeRepo],
        amocrm_group_status_repo: type[AmocrmGroupStatusRepo],
        price_offer_matrix_repo: type[payment_repos.PriceOfferMatrixRepo]
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.booking_tag_repo: BookingTagRepo = booking_tag_repo()
        self.booking_type_repo: BuildingBookingTypeRepo = booking_type_repo()
        self.price_offer_matrix_repo: payment_repos.PriceOfferMatrixRepo = price_offer_matrix_repo()
        self.amocrm_group_status_repo: AmocrmGroupStatusRepo = (
            amocrm_group_status_repo()
        )
        self.session: BookingSession = session
        self.document_key: str = session_config["document_key"]

    async def __call__(self, booking_id: int, user_id: int) -> Booking:
        filters: dict = dict(id=booking_id, user_id=user_id)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters,
            related_fields=[
                "project__city",
                "property__section",
                "property__property_type",
                "floor",
                "ddu",
                "agent",
                "agency",
                "booking_source",
            ],
            prefetch_fields=[
                "ddu__participants",
                "amocrm_status__group_status",
                "task_instances__status__buttons",
                "task_instances__status__tasks_chain__task_visibility",
                dict(
                    relation="building__booking_types",
                    queryset=self.booking_type_repo.list(),
                    to_attr="booking_types_by_building",
                ),
            ],
        )
        if not booking:
            raise BookingNotFoundError

        validated_price = None

        if booking.payment_amount is not None:
            validated_price = int(booking.payment_amount)
        elif booking.building and (booking.building.booking_price is not None):
            validated_price = int(booking.building.booking_price)

        price_offer: payment_repos.PriceOfferMatrix = await self.price_offer_matrix_repo.retrieve(
            filters=dict(
                payment_method_id=booking.amo_payment_method_id,
                mortgage_type_id=booking.mortgage_type_id,
            ),
        )
        if price_offer and price_offer.by_dev:
            booking.has_subsidy_price = True
        else:
            booking.has_subsidy_price = False

        document_info: dict = dict( 
            city=booking.project.city.slug if booking.project else None,
            address=booking.building.address if booking.building else None,
            price=validated_price, 
            period=booking.building.booking_period if booking.building else None,
            premise=booking.property.premise.label if booking.property else None,
        )
        await self._session_insert_document_info(document_info)

        if not booking.time_valid():
            if booking.booking_source and booking.booking_source.slug in [
                BookingCreatedSources.LK,
                BookingCreatedSources.FAST_BOOKING,
            ]:
                raise BookingTimeOutRepeatError
            # raise BookingTimeOutError

        if booking.amocrm_status:
            await self._set_group_statuses(booking=booking)

        booking.booking_tags = await self._get_booking_tags(booking)
        booking.tasks = await self._get_booking_tasks(booking=booking)
        await self._get_max_booking_type(booking=booking)
        booking: Booking = self._deactivated_booking_response(booking=booking)
        return booking

    def _deactivated_booking_response(self, booking: Booking) -> Booking:
        if not booking.active:
            booking.property = booking.building = booking.expires = booking.property = booking.tags = None
        return booking

    async def _get_booking_tags(self, booking: Booking) -> list[BookingTag] | None:
        tag_filters: dict = dict(
            is_active=True,
            group_statuses=booking.amocrm_status.group_status
            if booking.amocrm_status
            else None,
        )
        return (
            await self.booking_tag_repo.list(filters=tag_filters, ordering="-priority")
        ) or None

    async def _get_max_booking_type(self, booking: Booking) -> Booking:
        if booking.building is not None:
            booking_types: list[BuildingBookingType] = booking.building.booking_types_by_building
            if booking_types:
                booking.max_booking_period = max(
                    [booking_type.period for booking_type in booking_types]
                )
            else:
                booking.max_booking_period = None
        return booking

    async def _session_insert_document_info(self, document_info: dict) -> None:
        self.session[self.document_key]: dict = document_info
        await self.session.insert()

    async def _get_booking_tasks(self, booking: Booking) -> list[dict | None]:
        """Get booking tasks"""
        match booking.booking_source.slug:
            case BookingCreatedSources.FAST_BOOKING | BookingCreatedSources.LK_ASSIGN:
                task_chain_slug: str = FastBookingSlug.ACCEPT_OFFER.value
            case BookingCreatedSources.AMOCRM:
                task_chain_slug: str = FreeBookingSlug.ACCEPT_OFFER.value
            case _:
                task_chain_slug: str = OnlineBookingSlug.ACCEPT_OFFER.value

        tasks: list[dict[str, Any] | None] = await get_booking_tasks(
            booking_id=booking.id,
            task_chain_slug=task_chain_slug,
        )
        return tasks

    async def _clear_tasks(self, tasks: list[dict[str, Any] | None]) -> list[dict[str, Any]]:
        banned_statuses: list[str] = [
            OnlineBookingSlug.PAYMENT_SUCCESS.value,
            FastBookingSlug.PAYMENT_SUCCESS.value,
            FreeBookingSlug.PAYMENT_SUCCESS.value,
        ]
        return [
            task for task in tasks
            if task["task_status"] not in banned_statuses
        ]

    async def _get_task_chain_statuses(self, status: str) -> list[TaskStatus] | None:
        task_chain = await get_interesting_task_chain(status=status)
        statuses: list[TaskStatus] = sorted(
            task_chain.task_statuses, key=lambda x: x.priority
        )
        return statuses

    async def _set_group_statuses(self, booking: Booking) -> None:
        group_statuses: list[
            AmocrmGroupStatus
        ] = await self.amocrm_group_status_repo.list(
            filters=dict(is_final=False),
            ordering="sort",
        )
        final_group_statuses: list[
            AmocrmGroupStatus
        ] = await self.amocrm_group_status_repo.list(
            filters=dict(is_final=True),
        )
        final_group_statuses_ids = [
            final_group_status.id for final_group_status in final_group_statuses
        ]

        booking_group_status = booking.amocrm_status.group_status
        if not booking_group_status:
            booking_group_status_current_step = 1
        elif booking_group_status.id in final_group_statuses_ids:
            booking_group_status_current_step = len(group_statuses) + 1
        else:
            for number, group_status in enumerate(group_statuses):
                if booking_group_status.id == group_status.id:
                    booking_group_status_current_step = number + 1

        booking_group_status_actions = (
            await booking_group_status.amocrm_actions if booking_group_status else None
        )

        if booking_group_status:
            booking.amocrm_status.name = booking_group_status.name
            booking.amocrm_status.group_id = booking_group_status.id
            booking.amocrm_status.show_reservation_date = (
                booking_group_status.show_reservation_date
            )
            booking.amocrm_status.show_booking_date = (
                booking_group_status.show_booking_date
            )

        booking.amocrm_status.color = (
            booking_group_status.color if booking_group_status else None
        )
        booking.amocrm_status.steps_numbers = len(group_statuses) + 1
        booking.amocrm_status.current_step = booking_group_status_current_step
        booking.amocrm_status.actions = booking_group_status_actions
