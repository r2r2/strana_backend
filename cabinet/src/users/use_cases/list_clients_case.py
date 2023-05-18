from datetime import datetime
from typing import Any, List, Optional, Type, Union

from src.users.entities import BaseUserCase
from src.users.repos import User, UserRepo
from src.users.types import UserPagination
from tortoise.query_utils import Q

from ..constants import UserType
from ..exceptions import UserNoAgencyError, UserNotFoundError


class ListClientsCase(BaseUserCase):
    """Получение выборки клиентов для представителя агентства"""
    def __init__(
        self,
        user_repo: Type[UserRepo]
    ):
        self.user_repo = user_repo()

    async def __call__(
        self,
        *,
        init_filters: dict,
        pagination: UserPagination,
        repres_id: Optional[int] = None,
        agent_id: Optional[int] = None,
    ):
        if repres_id:
            repres: User = await self.user_repo.retrieve(filters=dict(id=repres_id))
            if not repres:
                raise UserNotFoundError
            agency_id = repres.maintained_id
            if not agency_id:
                raise UserNoAgencyError
            additional_filters = dict(agency_id=agency_id, type=UserType.CLIENT)
        elif agent_id:
            agent: User = await self.user_repo.retrieve(filters=dict(id=agent_id))
            if not agent:
                raise UserNotFoundError
            additional_filters = dict(agent_id=agent_id, type=UserType.CLIENT)
        else:
            additional_filters = dict(type=UserType.CLIENT)
        q_filters = self._get_work_period_q_filters(init_filters)
        init_filters.update(additional_filters)
        users: List[User] = await self.user_repo.list(
            filters=init_filters,
            q_filters=q_filters,
            end=pagination.end,
            start=pagination.start,
            prefetch_fields=[
                "agent",
                "agent__agency",
                "users_checks",
                "bookings",
                "agency"
            ]
        )
        counted: list[tuple[Union[int, str]]] = await self.user_repo.count(
            filters=init_filters,
            q_filters=q_filters
        )
        count = self._get_count(counted)
        self._set_related_objects(users)
        data: dict[str, Any] = dict(count=count, result=users, page_info=pagination(count=count))

        return data

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
            Q(work_end__isnull=False) & Q(work_start__lte=work_start) & Q(work_end__gte=work_start),
            # work end between u_start and u_end
            Q(work_end__isnull=False) & Q(work_start__lte=work_end) & Q(work_end__gte=work_end),
            # work start less u_start and work end greater u_end
            Q(work_end__isnull=False) & Q(work_start__gte=work_start) & Q(work_end__lte=work_end),

            Q(work_end__isnull=True) & Q(work_start__lte=work_end)
        ]

        return [self.user_repo.q_builder(or_filters=or_filters)]

    def _set_related_objects(self, users: List[User]) -> None:
        """Добавляем аттрибуты для отрисовки pydantic-моделями"""

        for user in users:
            setattr(user, "checks", user.users_checks.related_objects)
            setattr(user, "bookings_list", user.bookings.related_objects)

    def _get_count(self, counted: List[Any]) -> int:
        """Получение кол-ва записей для пагинации"""
        count: int = len(counted)
        if count and count == 1:
            count: int = counted[0][0]
        return count
