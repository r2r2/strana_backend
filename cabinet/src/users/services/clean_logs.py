from copy import copy
from datetime import datetime, timedelta
from typing import Type

from tortoise import Tortoise

from src.booking.repos import BookingLogRepo
from src.agencies.repos import AgencyLogRepo
from ..entities import BaseUserService
from ..repos import UserLogRepo


class CleanLogsService(BaseUserService):
    """
    Сервис очистки логов
    """
    def __init__(
            self,
            user_log_repo: Type[UserLogRepo],
            booking_log_repo: Type[BookingLogRepo],
            agency_log_repo: Type[AgencyLogRepo],
            orm_class: Type[Tortoise],
            orm_config: dict,
    ) -> None:
        self.user_log_repo: UserLogRepo = user_log_repo()
        self.booking_log_repo: BookingLogRepo = booking_log_repo()
        self.agency_log_repo: AgencyLogRepo = agency_log_repo()
        self.orm_class = orm_class
        self.orm_config = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(self, days: int):
        threshold: datetime = datetime.now() - timedelta(days=days)
        clean_logs_filters: dict = dict(created__lte=threshold)
        await self.user_log_repo.list(filters=clean_logs_filters).delete()
        await self.booking_log_repo.list(filters=clean_logs_filters).delete()
        await self.agency_log_repo.list(filters=clean_logs_filters).delete()
