from typing import Any, Type, Union, Optional

from ..constants import UserType
from ..entities import BaseUserCase
from ..mixins import CurrentUserDataMixin
from ..repos import UserRepo, CheckRepo, User
from ..types import UserBookingRepo, UserPagination


class UsersListCase(BaseUserCase, CurrentUserDataMixin):
    """
    Кейс для списка пользователей
    """

    def __init__(
        self,
        user_repo: Type[UserRepo],
        check_repo: Type[CheckRepo],
        booking_repo: Type[UserBookingRepo],
        user_type: Union[UserType.AGENT, UserType.REPRES, UserType.ADMIN]
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.check_repo: CheckRepo = check_repo()
        self.booking_repo: UserBookingRepo = booking_repo()
        self.user_type: Union[UserType.AGENT, UserType.REPRES, UserType.ADMIN] = user_type

    async def __call__(self,
                       init_filters: dict[str, Any],
                       pagination: UserPagination,
                       agency_id: Optional[int] = None,
                       agent_id: Optional[int] = None
                       ) -> dict[str, Any]:
        self.init_user_data(agent_id=agent_id, agency_id=agency_id)
        ordering: Union[str, None] = init_filters.pop("ordering", "-created")
        search: list[list[dict[str, Any]]] = init_filters.pop("search", list())

        check_qs: Any = self.check_repo.list(ordering='-id', related_fields=["unique_status"])

        prefetch_fields: list[Union[str, dict[str, Any]]] = [
            "agent",
            "agency",
            dict(relation="users_checks", queryset=check_qs, to_attr="checks"),
        ]
        filters: dict[str, Any] = self.get_user_filters(init_filters=init_filters)
        annotations: dict[str, Any] = self.get_user_annotations()
        q_filters = self.get_user_q_filters(search)
        users: list[User] = await self.user_repo.list(
            filters=filters,
            ordering=ordering,
            end=pagination.end,
            q_filters=q_filters,
            start=pagination.start,
            annotations=annotations,
            prefetch_fields=prefetch_fields,
        )
        counted: list[tuple[Union[int, str]]] = await self.user_repo.count(
            filters=filters, q_filters=q_filters
        )
        count: int = len(counted)
        if count and count == 1:
            count: int = counted[0][0]
        data: dict[str, Any] = dict(count=count, result=users, page_info=pagination(count=count))
        return data

    def get_user_filters(self, init_filters: dict):
        """Get user data with user_data mixin"""

        filters = dict(type=UserType.CLIENT, **init_filters)
        if self.user_type == UserType.AGENT:
            filters["checkers"] = self.current_user_data.agent_id
        if self.user_type == UserType.REPRES:
            filters["agency"] = self.current_user_data.agency_id
        return filters

    def get_user_annotations(self) -> dict[str, Any]:
        """Get user annotations"""

        filters: dict[str, Any] = dict(
            active=True, user_id=self.user_repo.a_builder.build_outer("id"),
            **self.current_user_data.dict(exclude_none=True)
        )
        booking_scount: Any = self.booking_repo.scount(filters=filters)
        filters["decremented"]: bool = True
        booking_exists: Any = self.booking_repo.exists(filters=filters)
        filters = dict(bookings__active=True)
        if self.user_type == UserType.AGENT:
            filters["bookings__agent_id"] = self.current_user_data.agent_id
        if self.user_type == UserType.REPRES:
            filters['bookings__agency_id'] = self.current_user_data.agency_id
        annotations: dict[str, Any] = dict(
            commission_avg=self.user_repo.a_builder.build_avg(
                "bookings__commission",
                self.user_repo.q_builder(and_filters=[filters]),
            ),
            commission_sum=self.user_repo.a_builder.build_sum(
                "bookings__commission_value",
                self.user_repo.q_builder(and_filters=[filters]),
            ),
            is_decremented=self.user_repo.a_builder.build_exists(booking_exists),
            booking_count=self.user_repo.a_builder.build_subquery(booking_scount),
            created=self.user_repo.a_builder.build_max(
                'bookings__created',
                self.user_repo.q_builder(and_filters=[filters]),
            )
        )
        return annotations

    def get_user_q_filters(self, search: list) -> list[Any]:
        """Get query filters for user"""

        if len(search) == 1:
            return [self.user_repo.q_builder(or_filters=search[0])]
        q_base: Any = self.user_repo.q_builder()
        for s in search:
            q_base |= self.user_repo.q_builder(and_filters=s)
        return [q_base]
