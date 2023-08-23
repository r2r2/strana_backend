from datetime import datetime, time
from typing import Type, Optional

from tortoise.functions import Count, Q
from tortoise.queryset import QuerySet

from common.paginations import PagePagination
from src.users.constants import UserStatus
from src.users.entities import BaseUserCase
from src.users.models import HistoryCheckSearchFilters
from src.users.repos import CheckHistory, CheckHistoryRepo, UniqueStatus
from src.users.utils import get_unique_status


class AdminChecksHistoryCase(BaseUserCase):
    """Получение выборки клиентов для представителя агентства"""
    def __init__(self, history_check_repo: Type[CheckHistoryRepo]):
        self.history_check_repo: CheckHistoryRepo = history_check_repo()

    async def __call__(
            self,
            *,
            status_types: Optional[list[str]],
            init_filters: HistoryCheckSearchFilters,
            pagination: PagePagination
    ):
        filters: dict = self._get_filters(init_filters, status_types)
        q_filters: list[Optional[dict]] = self._get_or_filters(init_filters.search)
        ordering = init_filters.ordering.value if init_filters.ordering else "id"
        prefetch_fields: list[str] = [
            "client",
            "agent",
            "agency",
        ]
        status_error: UniqueStatus = await get_unique_status(slug=UserStatus.ERROR)
        check_history_qs: QuerySet = self.history_check_repo.list(
            filters=filters,
            q_filters=q_filters,
            prefetch_fields=prefetch_fields,
            ordering=ordering,
            start=pagination.start,
            end=pagination.end,
        ).exclude(unique_status=status_error)

        check_history_count_qs: QuerySet = self.history_check_repo.list(
            filters=filters,
            q_filters=q_filters,
            prefetch_fields=prefetch_fields,
        ).exclude(unique_status=status_error)

        count: int = await check_history_count_qs.count()

        check_history: list[CheckHistory] = await check_history_qs
        aggregators: list[dict] = await self._get_aggregators(check_history_count_qs)
        data: dict = dict(
            count=count,
            aggregators=aggregators,
            result=check_history,
            page_info=pagination(count=count)
        )
        return data

    def _get_filters(self, init_filters: HistoryCheckSearchFilters, status_types: Optional[list[str]]):
        """
        Получение жёстких фильтров
        """
        filters: dict = dict()
        if status_types:
            filters["status__in"] = status_types
        if init_filters.start_date:
            filters["created_at__gte"] = init_filters.start_date
        if init_filters.end_date:
            filters["created_at__lte"] = datetime.combine(init_filters.end_date, time.max)
        return filters

    def _get_or_filters(self, search: str):
        """
        Получение гибких фильтров
        """
        q_filters: list = []
        if search and search.isdigit():
            or_filters = [
                dict(client_id__icontains=int(search)),
                dict(agent_id__icontains=int(search)),
                dict(agency_id=int(search)),
                dict(client__amocrm_id__icontains=int(search)),
                dict(agent__amocrm_id__icontains=int(search)),
                dict(agency__amocrm_id__icontains=int(search)),
            ]
            q_filters: list = [self.history_check_repo.q_builder(or_filters=or_filters)]
        elif search:
            or_filters: list[dict] = [
                # поиск по полям клиента
                dict(client__name__icontains=search),
                dict(client__surname__icontains=search),
                dict(client__patronymic__icontains=search),
                dict(client__phone__icontains=search),
                dict(client_phone__icontains=search),
                dict(client__email__icontains=search),

                # поиск по полям агента
                dict(agent__name__icontains=search),
                dict(agent__surname__icontains=search),
                dict(agent__patronymic__icontains=search),
                dict(agent__phone__icontains=search),
                dict(agent__email__icontains=search),

                # поиск по полям агентства
                dict(agency__name__icontains=search),
            ]
            q_filters: list = [self.history_check_repo.q_builder(or_filters=or_filters)]
        return q_filters

    async def _get_aggregators(self, check_history_qs: QuerySet) -> dict[str:int]:
        """
        Получение агрегаторов
        """
        total_aggregators: dict = dict()
        # todo: We can refactor it to one query
        status_unique: UniqueStatus = await get_unique_status(slug=UserStatus.UNIQUE)
        status_not_unique: UniqueStatus = await get_unique_status(slug=UserStatus.NOT_UNIQUE)
        status_can_dispute: UniqueStatus = await get_unique_status(slug=UserStatus.CAN_DISPUTE)

        aggregators: list[dict] = await check_history_qs.annotate(
            unique_count=Count('unique_status_id', _filter=Q(unique_status=status_unique)),
            not_unique_count=Count('unique_status_id', _filter=Q(unique_status=status_not_unique)),
            can_dispute_count=Count('unique_status_id', _filter=Q(unique_status=status_can_dispute)),
        ).values('unique_count', 'not_unique_count', 'can_dispute_count')

        for aggregator in aggregators:
            for key, value in aggregator.items():
                total_aggregators[key] = total_aggregators.get(key, 0) + value

        return total_aggregators
