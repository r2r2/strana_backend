from datetime import datetime, time
from typing import Any, List, Type, Union

from src.booking.constants import BookingSubstages
from src.users.entities import BaseUserCase
from src.users.repos import CheckRepo, User, UserRepo
from src.users.types import UserPagination
from tortoise.query_utils import Q

from ..constants import UserType


class AdminListClientsCase(BaseUserCase):
    """Получение выборки клиентов для представителя агентства"""
    def __init__(
        self,
        user_repo: Type[UserRepo],
        check_repo: Type[CheckRepo]
    ):
        self.user_repo = user_repo()
        self.check_repo = check_repo()

    async def __call__(
        self,
        *,
        init_filters: dict,
        pagination: UserPagination,
    ):
        additional_filters = dict(type=UserType.CLIENT)
        search = init_filters.pop("search", [])
        ordering = init_filters.pop("ordering", "name")
        init_filters.update(additional_filters)

        q_filters = self._get_work_period_q_filters(init_filters)
        if search:
            search_q_filters: list[Any] = [self.user_repo.q_builder(or_filters=search[0])]
            q_filters += search_q_filters

        bookings_count_annotations: dict[str, Any] = self._get_booking_count_annotation()
        users: List[User] = await self.user_repo.list(
            filters=init_filters,
            q_filters=q_filters,
            end=pagination.end,
            start=pagination.start,
            ordering=ordering,
            annotations=bookings_count_annotations,
            prefetch_fields=[
                "agent",
                "agency",
                "bookings",
                dict(relation="users_checks",
                     queryset=self.check_repo.list(ordering="-requested"),
                     to_attr="statuses")
            ],
        )
        counted: list[tuple[Union[int, str]]] = await self.user_repo.count(
            filters=init_filters,
            q_filters=q_filters
        )
        count = self._get_count(counted)
        for user in users:
            user.status = next(iter(user.statuses), None)
        data: dict[str, Any] = dict(count=count, result=users, page_info=pagination(count=count))

        return data

    def _get_booking_count_annotation(self) -> dict[str, Any]:
        """Get bookings annotations"""
        bookings = self.user_repo.a_builder.build_count(
            "bookings"
        )
        active_bookings = self.user_repo.a_builder.build_count(
            "bookings",
            filter=~Q(bookings__amocrm_substage__in=[BookingSubstages.REALIZED, BookingSubstages.UNREALIZED]),
        )
        successful_bookings = self.user_repo.a_builder.build_count(
            "bookings", filter=Q(bookings__amocrm_substage=BookingSubstages.REALIZED)
        )
        unsuccessful_bookings = self.user_repo.a_builder.build_count(
            "bookings", filter=Q(bookings__amocrm_substage=BookingSubstages.UNREALIZED)
        )

        bookings_count: dict[str, Any] = dict(
            bookings_count=bookings,
            active_bookings_count=active_bookings,
            successful_bookings_count=successful_bookings,
            unsuccessful_bookings_count=unsuccessful_bookings,
        )
        return bookings_count

    def _get_work_period_q_filters(self, init_filter: dict) -> Any:
        """Create query filters for period of work
        Side effect: deletes keys 'work_start__lte' and 'work_end__gte'
        """
        # если у пользователя work_end null, надо считать что это inf и заложиться под это фильтрами
        or_filters = []
        try:
            work_start = datetime.combine(init_filter.pop("work_start"), time.max)
        except KeyError:
            return [self.user_repo.q_builder()]

        try:
            work_end = datetime.combine(init_filter.pop("work_end"), time.max)
        except KeyError:
            work_end = datetime.max
            or_filters += [Q(work_end__isnull=True)]

        or_filters += [
            # work start between u_start and u_end
            Q(work_end__isnull=False) & Q(work_start__lte=work_start) & Q(work_end__gte=work_start),
            # work end between u_start and u_end
            Q(work_end__isnull=False) & Q(work_start__lte=work_end) & Q(work_end__gte=work_end),
            # work start less u_start and work end greater u_end
            Q(work_end__isnull=False) & Q(work_start__gte=work_start) & Q(work_end__lte=work_end),

            Q(work_end__isnull=True) & Q(work_start__lte=work_end)
        ]

        return [self.user_repo.q_builder(or_filters=or_filters)]

    def _get_count(self, counted: List[Any]) -> int:
        """Получение кол-ва записей для пагинации"""
        count: int = len(counted)
        if count and count == 1:
            count: int = counted[0][0]
        return count
