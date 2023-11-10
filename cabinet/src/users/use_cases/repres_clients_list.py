from datetime import datetime
from typing import Any, List, Type, Union

from src.booking.constants import BookingSubstages
from src.users.entities import BaseUserCase
from src.users.repos import CheckRepo, User, UserRepo, UserPinningStatusRepo
from src.users.types import UserPagination
from tortoise.expressions import Q

from ..constants import UserType
from ..exceptions import UserNoAgencyError, UserNotFoundError


class RepresListClientsCase(BaseUserCase):
    """Получение выборки клиентов для представителя агентства"""

    def __init__(
        self,
        user_repo: Type[UserRepo],
        check_repo: Type[CheckRepo],
        user_pinning_repo: Type[UserPinningStatusRepo],
    ):
        self.user_repo = user_repo()
        self.check_repo = check_repo()
        self.user_pinning_repo = user_pinning_repo()

    async def __call__(
        self,
        *,
        init_filters: dict,
        pagination: UserPagination,
        repres_id: int,
    ):
        search = init_filters.pop("search", [])
        ordering = init_filters.pop("ordering", "-id")
        booking_active_status = init_filters.pop("is_active", None)

        repres: User = await self.user_repo.retrieve(filters=dict(id=repres_id))
        if not repres:
            raise UserNotFoundError
        agency_id = repres.maintained_id
        if not agency_id:
            raise UserNoAgencyError

        additional_filters = dict(
            agency_id=agency_id,
            type=UserType.CLIENT,
        )
        init_filters.update(additional_filters)

        q_filters = self._get_work_period_q_filters(init_filters)
        if search:
            search_q_filters: list[Any] = [
                self.user_repo.q_builder(or_filters=search[0])
            ]
            q_filters += search_q_filters

        bookings_count_annotations: dict[str, Any] = self._get_booking_count_annotation(
            agency_id
        )
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
                dict(
                    relation="users_checks",
                    queryset=self.check_repo.list(
                        ordering="-requested", related_fields=["unique_status"]
                    ),
                    to_attr="statuses",
                ),
                dict(
                    relation="users_pinning_status",
                    queryset=self.user_pinning_repo.list(
                        related_fields=["unique_status"]
                    ),
                    to_attr="pinning_statuses",
                ),
            ],
        )
        count: int  = await self.user_repo.count(
            filters=init_filters, q_filters=q_filters
        )
        for user in users:
            user.status = next(iter(user.statuses), None)
            user.pinning_status = next(iter(user.pinning_statuses), None)

        list_to_remove_users = list()
        if booking_active_status is None:
            for user in users:
                if user.active_bookings_count == 0:
                    user.pinning_status = None
        elif booking_active_status is False:
            for user in users:
                if user.active_bookings_count > 0:
                    count -= 1
                    list_to_remove_users.append(user)
                else:
                    user.pinning_status = None
        else:
            for user in users:
                if user.active_bookings_count == 0:
                    count -= 1
                    list_to_remove_users.append(user)

        result_users = [user for user in users if user not in list_to_remove_users]

        data: dict[str, Any] = dict(
            count=count, result=result_users, page_info=pagination(count=count)
        )

        return data

    def _get_booking_count_annotation(self, agency_id) -> dict[str, Any]:
        """Get bookings annotations"""
        bookings = self.user_repo.a_builder.build_count(
            "bookings",
            filter=Q(bookings__agency_id=agency_id),
        )
        active_bookings = self.user_repo.a_builder.build_count(
            "bookings",
            filter=~Q(
                bookings__amocrm_substage__in=[
                    BookingSubstages.REALIZED,
                    BookingSubstages.UNREALIZED,
                ]
            )
            & Q(bookings__agency_id=agency_id),
        )
        successful_bookings = self.user_repo.a_builder.build_count(
            "bookings",
            filter=Q(bookings__amocrm_substage=BookingSubstages.REALIZED)
            & Q(bookings__agency_id=agency_id),
        )
        unsuccessful_bookings = self.user_repo.a_builder.build_count(
            "bookings",
            filter=Q(bookings__amocrm_substage=BookingSubstages.UNREALIZED)
            & Q(bookings__agency_id=agency_id),
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
        # техдолг: Продумать подмену user__work_end=null на user__work_end=date.max
        or_filters = []
        try:
            work_start = init_filter.pop("work_start")
        except KeyError:
            return [self.user_repo.q_builder()]

        try:
            work_end = init_filter.pop("work_end")
        except KeyError:
            work_end = datetime.max
            or_filters += [Q(work_end__isnull=True)]

        or_filters += [
            # work start between u_start and u_end
            Q(work_end__isnull=False)
            & Q(work_start__lte=work_start)
            & Q(work_end__gte=work_start),
            # work end between u_start and u_end
            Q(work_end__isnull=False)
            & Q(work_start__lte=work_end)
            & Q(work_end__gte=work_end),
            # work start less u_start and work end greater u_end
            Q(work_end__isnull=False)
            & Q(work_start__gte=work_start)
            & Q(work_end__lte=work_end),
            Q(work_end__isnull=True) & Q(work_start__lte=work_end),
        ]

        return [self.user_repo.q_builder(or_filters=or_filters)]
