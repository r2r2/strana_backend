import datetime
from typing import Any, Optional, Type, Union

from tortoise.query_utils import Q

from ...amocrm.repos import AmocrmStatusRepo
from ...booking.repos import Booking
from ..constants import UserType
from ..entities import BaseUserCase
from ..mixins import CurrentUserDataMixin
from ..repos import CheckRepo, UserRepo
from ..types import UserBookingRepo, UserPagination
from ...task_management.repos import TaskInstance
from ...task_management.utils import build_task_data


class UsersBookingsCase(BaseUserCase, CurrentUserDataMixin):
    """
    Кейс для списка пользователей
    """

    def __init__(
        self,
        user_repo: Type[UserRepo],
        check_repo: Type[CheckRepo],
        booking_repo: Type[UserBookingRepo],
        amocrm_status_repo: Type[AmocrmStatusRepo],
        user_type: Union[UserType.AGENT, UserType.REPRES, UserType.ADMIN]
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.amocrm_status_repo: AmocrmStatusRepo = amocrm_status_repo()
        self.check_repo: CheckRepo = check_repo()
        self.booking_repo: UserBookingRepo = booking_repo()
        self.user_type: Union[UserType.AGENT, UserType.REPRES, UserType.ADMIN] = user_type

    async def __call__(
            self,
            init_filters: dict[str, Any],
            pagination: UserPagination,
            agency_id: Optional[int] = None,
            agent_id: Optional[int] = None
    ) -> dict[str, Any]:
        self.init_user_data(agent_id=agent_id, agency_id=agency_id)
        ordering: Union[str, None] = init_filters.pop("ordering", "-id")
        search: list[list[dict[str, Any]]] = init_filters.pop("search", [])

        prefetch_fields: list[Union[str, dict[str, Any]]] = [
            "agent",
            "agency",
            "user",
            "project",
            "building",
            "property",
            "property__floor",
            "amocrm_status",
            "amocrm_status__group_status",
            "task_instances",
            "task_instances__status",
            "task_instances__status__button",
            "task_instances__status__tasks_chain__task_visibility",
        ]
        q_filters = self.get_booking_q_filters(search)
        q_filters += self.get_work_period_q_filters(init_filters)
        filters: dict[str, Any] = self.get_bookings_filters(init_filters=init_filters)

        bookings: list[Booking] = await self.booking_repo.list(
            filters=filters,
            ordering=ordering,
            end=pagination.end,
            q_filters=q_filters,
            start=pagination.start,
            prefetch_fields=prefetch_fields,
        )
        count: int = await self.booking_repo.scount(
            filters=filters, q_filters=q_filters
        )

        for booking in bookings:
            booking.tasks = await self._get_booking_tasks(booking=booking)

            if booking.project and booking.amocrm_status:
                statuses = await self.amocrm_status_repo.list(
                    filters=dict(pipeline_id=booking.project.amo_pipeline_id),
                    ordering="sort",
                )
                booking.amocrm_status.steps_numbers = len(statuses) + 1
                statuses.append(booking.amocrm_status)
                booking.amocrm_status.current_step = statuses.index(booking.amocrm_status) + 1

        data: dict[str, Any] = dict(count=count, result=bookings, page_info=pagination(count=count))
        return data

    def get_bookings_filters(self, init_filters: dict) -> dict[str, Any]:
        """Get booking data with user_data mixin"""

        filters = dict(user__type=UserType.CLIENT, **init_filters)
        if self.user_type == UserType.AGENT:
            filters["agent_id"] = self.current_user_data.agent_id
        if self.user_type == UserType.REPRES:
            filters["agency_id"] = self.current_user_data.agency_id

        return filters

    def get_booking_q_filters(self, search: list) -> list[Any]:
        """Get query filters for booking"""

        if len(search) == 1:
            return [self.booking_repo.q_builder(or_filters=search[0])]
        q_base: Any = self.booking_repo.q_builder()
        for s in search:
            q_base |= self.booking_repo.q_builder(and_filters=s)
        return [q_base]

    def get_work_period_q_filters(self, init_filter: dict) -> Any:
        """Create query filters for period of work
        Side effect: deletes keys 'user__work_start__lte' and 'user__work_end__gte'
        """
        # если у пользователя work_end null, надо считать что это inf и заложиться под это фильтрами
        # техдолг: Продумать подмену user__work_end=null на user__work_end=date.max
        or_filters = []
        try:
            work_start = init_filter.pop("user__work_start")
        except KeyError:
            return [self.booking_repo.q_builder()]

        try:
            work_end = init_filter.pop("user__work_end")
        except KeyError:
            work_end = datetime.datetime.max
            or_filters += [Q(user__work_end__isnull=True)]

        or_filters += [
            # work start between u_start and u_end
            Q(user__work_end__isnull=False) & Q(user__work_start__lte=work_start) & Q(user__work_end__gte=work_start),
            # work end between u_start and u_end
            Q(user__work_end__isnull=False) & Q(user__work_start__lte=work_end) & Q(user__work_end__gte=work_end),
            # work start less u_start and work end greater u_end
            Q(user__work_end__isnull=False) & Q(user__work_start__gte=work_start) & Q(user__work_end__lte=work_end),

            Q(user__work_end__isnull=True) & Q(user__work_start__lte=work_end)
        ]

        return [self.booking_repo.q_builder(or_filters=or_filters)]

    async def _get_booking_tasks(self, booking: Booking) -> list[TaskInstance]:
        """Get booking tasks"""
        tasks = []
        # берем все таски, которые видны в текущем статусе букинга
        task_instances: list[TaskInstance] = [
            task for task in booking.task_instances if booking.amocrm_status in task.status.tasks_chain.task_visibility
        ]
        if task_instances:
            # берем таску с наивысшим приоритетом,
            # наивысшим будет приоритет с наименьшим значением ¯_(ツ)_/¯
            highest_priority_task = min(task_instances, key=lambda x: x.status.priority)
            tasks = build_task_data(task_instances=[highest_priority_task], booking_status=booking.amocrm_status)
        return tasks
