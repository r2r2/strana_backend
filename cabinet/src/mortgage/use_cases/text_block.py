import asyncio
from typing import Any

from tortoise.queryset import QuerySet

from common.sentry.utils import send_sentry_log
from src.cities.repos import CityRepo
from src.mortgage.entities import BaseMortgageCase
from src.mortgage.repos import MortgageTextBlockRepo, MortgageTextBlock


class GetMortgageTextBlockCase(BaseMortgageCase):
    """
    Получение текстовых блоков для ипотеки
    """

    def __init__(
        self,
        mortgage_text_block_repo: type[MortgageTextBlockRepo],
        city_repo: type[CityRepo],
    ):
        self.mortgage_text_block_repo: MortgageTextBlockRepo = mortgage_text_block_repo()
        self.city_repo: CityRepo = city_repo()

    async def __call__(self, city_slug: str) -> MortgageTextBlock | None:
        city_qs: QuerySet = (
            self.city_repo.list(
                filters=dict(slug=city_slug),
            )
            .values("id")
            .as_query()
        )
        text_block: MortgageTextBlock | None = await self.mortgage_text_block_repo.retrieve(
            filters=dict(cities__id__in=city_qs),
            prefetch_fields=['cities'],
        )
        if not text_block:
            await self._send_sentry_log(city_slug=city_slug)
        return text_block

    async def _send_sentry_log(self, city_slug: str) -> None:
        sentry_ctx: dict[str, Any] = dict(
            city_slug=city_slug,
        )
        _: asyncio.Task = asyncio.create_task(
            send_sentry_log(
                tag=self.__class__.__name__,
                message=f"Не найден текстовый блок для слага города {city_slug=}",
                context=sentry_ctx,
            )
        )
