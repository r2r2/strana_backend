from src.amocrm.repos import AmocrmGroupStatus, AmocrmGroupStatusRepo
from src.task_management.constants import OnlineBookingSlug
from src.task_management.repos import TaskStatus
from src.task_management.utils import (
    is_task_in_compare_task_chain,
    get_interesting_task_chain,
    TaskDataBuilder,
)
from src.buildings.repos import BuildingBookingType, BuildingBookingTypeRepo
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
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.booking_tag_repo: BookingTagRepo = booking_tag_repo()
        self.booking_type_repo: BuildingBookingTypeRepo = booking_type_repo()
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
                    to_attr="booking_types_by_building"
                ),
            ],
        )
        if not booking:
            raise BookingNotFoundError

        document_info: dict = dict(
            city=booking.project.city.slug if booking.project else None,
            address=booking.building.address if booking.building else None,
            price=booking.building.booking_price if booking.building else None,
            period=booking.building.booking_period if booking.building.booking_period else None,
            premise=booking.property.premise.label if booking.property else None,
        )
        await self._session_insert_document_info(document_info)

        if not booking.time_valid():
            if booking.booking_source and booking.booking_source.slug in [BookingCreatedSources.LK]:
                raise BookingTimeOutRepeatError
            raise BookingTimeOutError

        if booking.amocrm_status:
            await self._set_group_statuses(booking=booking)

        booking.booking_tags = await self._get_booking_tags(booking)
        booking.tasks = await self._get_booking_tasks(booking=booking)
        await self._get_max_booking_type(booking=booking)
        return booking

    async def _get_booking_tags(self, booking: Booking) -> list[BookingTag] | None:
        tag_filters: dict = dict(
            is_active=True,
            group_statuses=booking.amocrm_status.group_status if booking.amocrm_status else None,
        )
        return (await self.booking_tag_repo.list(filters=tag_filters, ordering="-priority")) or None

    async def _get_max_booking_type(self, booking: Booking) -> Booking:
        booking_types: list[BuildingBookingType] = booking.building.booking_types_by_building
        booking.max_booking_period = max([booking_type.period for booking_type in booking_types])
        return booking

    async def _session_insert_document_info(self, document_info: dict) -> None:
        self.session[self.document_key]: dict = document_info
        await self.session.insert()

    async def _get_booking_tasks(self, booking: Booking) -> list[dict | None]:
        """Get booking tasks"""
        online_booking_tasks = [
            task for task in booking.task_instances
            if await is_task_in_compare_task_chain(
                status=task.status, compare_status=OnlineBookingSlug.ACCEPT_OFFER.value
            )
        ]

        if not online_booking_tasks:
            return []

        tasks = await TaskDataBuilder(task_instances=online_booking_tasks, booking=booking).build()

        return tasks

    async def _set_group_statuses(self, booking: Booking) -> None:
        group_statuses: list[AmocrmGroupStatus] = await self.amocrm_group_status_repo.list(
            filters=dict(is_final=False),
            ordering="sort",
        )
        final_group_statuses: list[AmocrmGroupStatus] = await self.amocrm_group_status_repo.list(
            filters=dict(is_final=True),
        )
        final_group_statuses_ids = [final_group_status.id for final_group_status in final_group_statuses]

        booking_group_status = booking.amocrm_status.group_status
        if not booking_group_status:
            booking_group_status_current_step = 1
        elif booking_group_status.id in final_group_statuses_ids:
            booking_group_status_current_step = len(group_statuses) + 1
        else:
            for number, group_status in enumerate(group_statuses):
                if booking_group_status.id == group_status.id:
                    booking_group_status_current_step = number + 1

        booking_group_status_actions = await booking_group_status.amocrm_actions if booking_group_status else None

        if booking_group_status:
            booking.amocrm_status.name = booking_group_status.name
            booking.amocrm_status.group_id = booking_group_status.id
            booking.amocrm_status.show_reservation_date = booking_group_status.show_reservation_date
            booking.amocrm_status.show_booking_date = booking_group_status.show_booking_date

        booking.amocrm_status.color = booking_group_status.color if booking_group_status else None
        booking.amocrm_status.steps_numbers = len(group_statuses) + 1
        booking.amocrm_status.current_step = booking_group_status_current_step
        booking.amocrm_status.actions = booking_group_status_actions
