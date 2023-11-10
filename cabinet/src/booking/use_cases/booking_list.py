from src.task_management.constants import OnlineBookingSlug
from src.amocrm.repos import AmocrmGroupStatus, AmocrmGroupStatusRepo
from src.task_management.repos import TaskInstance
from src.task_management.utils import (
    is_task_in_compare_task_chain,
    TaskDataBuilder,
)
from src.payments import repos as payment_repos
from ..entities import BaseBookingCase
from ..models import BookingListFilters
from ..repos import Booking, BookingRepo, BookingTag, BookingTagRepo


class BookingListCase(BaseBookingCase):
    """
    Список бронирований
    """

    def __init__(
        self,
        booking_repo: type[BookingRepo],
        booking_tag_repo: type[BookingTagRepo],
        amocrm_group_status_repo: type[AmocrmGroupStatusRepo],
        price_offer_matrix_repo: type[payment_repos.PriceOfferMatrixRepo]
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.booking_tag_repo: BookingTagRepo = booking_tag_repo()
        self.amocrm_group_status_repo: AmocrmGroupStatusRepo = (
            amocrm_group_status_repo()
        )
        self.price_offer_matrix_repo: payment_repos.PriceOfferMatrixRepo = price_offer_matrix_repo()

    async def __call__(
        self,
        user_id: int,
        statuses: list,
        init_filters: BookingListFilters,
        property_types_filter: list,
    ) -> dict:
        filters: dict = dict(
            active=True,
            user_id=user_id,
            property_id__isnull=False,
            property__property_type__is_active=True,
            building_id__isnull=False,
            project_id__isnull=False,
        )
        additional_filters: dict = self._get_additional_filters(
            statuses=statuses,
            init_filters=init_filters,
            property_types_filter=property_types_filter,
        )
        filters.update(additional_filters)
        related_fields = [
            "property__section",
            "property__property_type",
            "floor",
            "building",
            "project",
            "ddu",
            "agent",
            "agency",
            "booking_source",
        ]
        bookings: list[Booking] = await self.booking_repo.list(
            filters=filters,
            related_fields=related_fields,
            prefetch_fields=[
                "amocrm_status__group_status",
                "task_instances__status__buttons",
                "task_instances__status__tasks_chain__task_visibility",
            ],
        )
        for booking in bookings:
            booking.tasks = await self._get_booking_tasks(booking=booking)

            if booking.amocrm_status:
                await self._set_group_statuses(booking=booking)
            booking.booking_tags = await self._get_booking_tags(booking)

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

        data: dict = dict(result=bookings, count=len(bookings))

        return data

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

    async def _get_booking_tasks(self, booking: Booking) -> list[TaskInstance | None]:
        """Get booking tasks"""
        tasks = []
        # берем все таски, которые видны в текущем статусе букинга
        task_instances: list[TaskInstance] = [
            task for task in booking.task_instances
            if booking.amocrm_status in task.status.tasks_chain.task_visibility
        ]
        for task in task_instances:
            if await is_task_in_compare_task_chain(
                status=task.status, compare_status=OnlineBookingSlug.ACCEPT_OFFER.value
            ):
                tasks = await TaskDataBuilder(
                    task_instances=task, booking=booking
                ).build()
                break
        return tasks

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
