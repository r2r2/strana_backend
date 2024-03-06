from typing import Any

from common.settings.repos import SystemList
from src.task_management.constants import OnlineBookingSlug, FastBookingSlug, FreeBookingSlug
from src.amocrm.repos import (
    AmocrmGroupStatus,
    AmocrmGroupStatusRepo,
    ClientAmocrmGroupStatusRepo,
    ClientAmocrmGroupStatus,
)
from src.task_management.utils import (
    get_booking_tasks,
    get_interesting_task_chain,
)
from src.booking.constants import BookingCreatedSources
from ..entities import BaseBookingCase
from ..models import BookingListFilters
from ..repos import Booking, BookingRepo, BookingTag, BookingTagRepo, BookingEventHistoryRepo
from src.task_management.repos import TaskChain
from src.properties.constants import PropertyTypes
from src.booking.utils import get_statuses_before_booking


class BookingHistoriesBookingListCase(BaseBookingCase):
    """
    Список бронирований у которых есть истории
    """

    def __init__(
        self,
        booking_repo: type[BookingRepo],
        booking_tag_repo: type[BookingTagRepo],
        amocrm_group_status_repo: type[AmocrmGroupStatusRepo],
        client_amocrm_group_status_repo: type[ClientAmocrmGroupStatusRepo],
        booking_event_history_repo: type[BookingEventHistoryRepo]
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.booking_tag_repo: BookingTagRepo = booking_tag_repo()
        self.amocrm_group_status_repo: AmocrmGroupStatusRepo = (
            amocrm_group_status_repo()
        )
        self.client_amocrm_group_status_repo: ClientAmocrmGroupStatusRepo = client_amocrm_group_status_repo()
        self.booking_event_history_repo: BookingEventHistoryRepo = booking_event_history_repo()

    async def __call__(
        self,
        user_id: int,
        statuses: list,
        init_filters: BookingListFilters,
        property_types_filter: list,
    ) -> dict:

        bookings: list[Booking] = await self._get_bookings(
            user_id=user_id,
            init_filters=init_filters,
            statuses=statuses,
            property_types_filter=property_types_filter,
        )

        for booking in bookings:
            booking.tasks = await self._get_booking_tasks(booking=booking)
            booking.client_group_statuses = await self._get_client_group_statuses(booking=booking)

            if booking.amocrm_status:
                await self._set_group_statuses(booking=booking)
            booking.booking_tags = await self._get_booking_tags(booking)

        data: dict = dict(result=bookings, count=len(bookings))

        return data

    async def _get_bookings(
        self,
        user_id: int,
        init_filters: BookingListFilters,
        statuses: list,
        property_types_filter: list,
    ) -> list[Booking]:

        filters = dict(booking_id__isnull=False)
        bookings_with_event_history = await self.booking_event_history_repo.list(
            filters=filters).distinct().values_list("booking_id", flat=True)

        filters: dict = dict(
            id__in=bookings_with_event_history,
            active=True,
            user_id=user_id,
        )
        additional_filters: dict = self._get_additional_filters(
            statuses=statuses,
            init_filters=init_filters,
            property_types_filter=property_types_filter,
        )
        filters.update(additional_filters)
        related_fields = [
            "property__section",
            "property__floor",
            "property__property_type",
            "floor",
            "building",
            "project",
            "ddu",
            "agent",
            "agency",
            "booking_source",
            "amo_payment_method",
            "mortgage_type",
        ]
        prefetch_fields = [
            "amocrm_status__group_status",
            "amocrm_status__client_group_status__task_chains",
        ]
        bookings: list[Booking] = await self.booking_repo.list(
            filters=filters,
            related_fields=related_fields,
            prefetch_fields=prefetch_fields,
            ordering="-created",
        )

        return bookings

    async def _get_booking_tags(self, booking: Booking) -> list[BookingTag] | None:
        group_statuses = booking.amocrm_status.group_status if booking.amocrm_status else None
        tag_filters: dict = dict(
            is_active=True,
            group_statuses=group_statuses,
        )
        return (
            await self.booking_tag_repo.list(filters=tag_filters, ordering="-priority")
        ) or None

    def _get_additional_filters(
        self,
        statuses: list,
        init_filters: BookingListFilters,
        property_types_filter: list,
    ) -> dict:
        additional_filters: dict = dict()
        if statuses:
            additional_filters.update(amocrm_stage__in=statuses)
        if property_types_filter:
            additional_filters.update(
                property__property_type__slug__in=property_types_filter
            )
        if init_filters:
            additional_filters.update(init_filters.dict(exclude_none=True))
        return additional_filters

    async def _get_booking_tasks(self, booking: Booking) -> list[dict[str, Any] | None]:
        """Get booking tasks"""
        task_chain_slug: str = await self._get_task_chain_slug(booking=booking)
        tasks: list[dict[str, Any] | None] = await get_booking_tasks(
            booking_id=booking.id,
            task_chain_slug=task_chain_slug,
        )
        tasks: list[dict | None] = await self._clear_tasks(tasks=tasks, booking=booking)
        return tasks

    async def _get_task_chain_slug(self, booking: Booking) -> str:
        """Get task chain slug"""
        if booking.booking_source is None:
            return OnlineBookingSlug.ACCEPT_OFFER.value

        match booking.booking_source.slug:
            case BookingCreatedSources.FAST_BOOKING | BookingCreatedSources.LK_ASSIGN:
                task_chain_slug: str = FastBookingSlug.ACCEPT_OFFER.value
            case BookingCreatedSources.AMOCRM:
                task_chain_slug: str = FreeBookingSlug.ACCEPT_OFFER.value
            case _:
                task_chain_slug: str = OnlineBookingSlug.ACCEPT_OFFER.value
        return task_chain_slug

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

    async def _get_client_group_statuses(self, booking: Booking) -> list[ClientAmocrmGroupStatus | None]:
        group_statuses: list[ClientAmocrmGroupStatus] = await self.client_amocrm_group_status_repo.list(
            filters=dict(is_hide=False),
            ordering="sort",
            prefetch_fields=[
                'booking_tags__booking_sources',
                'booking_tags__systems',
            ],
        )
        for status in group_statuses:
            status.tags = await self._get_client_group_status_tags(
                booking=booking,
                status=status,
            )
            match status:
                case booking.amocrm_status.client_group_status:
                    status.is_current = True
                case _:
                    status.is_current = False
        return group_statuses

    async def _get_client_group_status_tags(
        self,
        booking: Booking,
        status: ClientAmocrmGroupStatus,
    ) -> list[BookingTag]:
        """
        Ищем теги, которые подходят под источник бронирования и под системы.
        Систему ищем костыльно, через систему в цепочке задач,
        которая должна выводиться для этой брони.
        Так как брони с системой больше никак не связаны
        """
        task_chain_slug: str = await self._get_task_chain_slug(booking=booking)
        task_chain: TaskChain = await get_interesting_task_chain(status=task_chain_slug)
        await task_chain.fetch_related('systems')

        tags: list[BookingTag] = []
        for tag in status.booking_tags:
            common_booking_source: bool = booking.booking_source in tag.booking_sources
            common_systems: set[SystemList | None] = set(tag.systems).intersection(set(task_chain.systems))
            if common_booking_source and common_systems:
                tags.append(tag)
        return tags

    async def _clear_tasks(
        self,
        tasks: list[dict[str, Any] | None],
        booking: Booking,
    ) -> list[dict[str, Any] | None]:
        banned_statuses: set[str] = {
            OnlineBookingSlug.PAYMENT_SUCCESS.value,
            FastBookingSlug.PAYMENT_SUCCESS.value,
            FreeBookingSlug.PAYMENT_SUCCESS.value,
        }
        banned_properties_types: set[str] = {
            PropertyTypes.PARKING,
            PropertyTypes.PANTRY,
            PropertyTypes.COMMERCIAL,
        }

        cleared_tasks: list[dict | None] = []
        for task in tasks:
            task_chain: TaskChain = await get_interesting_task_chain(status=task["task_status"])

            valid_task_chain: bool = await self._is_valid_task_chain(
                task_chain=task_chain,
                booking=booking,
            )
            valid_task_status: bool = task["task_status"] not in banned_statuses
            valid_property_type: bool = booking.property.property_type.slug.upper() not in banned_properties_types

            if all((valid_task_chain, valid_task_status, valid_property_type)):
                cleared_tasks.append(task)
        return cleared_tasks

    async def _is_valid_task_chain(
        self,
        task_chain: TaskChain,
        booking: Booking,
    ) -> bool:
        """Проверяем, что сделка подходит под цепочку задач"""
        if booking.amocrm_status.client_group_status:
            return task_chain in booking.amocrm_status.client_group_status.task_chains
        # Если нет связи client_group_status, то предполагаем, что эта задача не должна выводиться в сделке
        return False
