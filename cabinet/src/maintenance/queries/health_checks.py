from typing import Type

from datetime import datetime, timedelta

from src.booking.repos import BookingPaymentsMaintenanceRepo
from src.users.repos import ClientCheckMaintenanceRepo, ClientAssignMaintenanceRepo
from ..entities import BaseMaintenanceQuery


class HealthCheckQueries(BaseMaintenanceQuery):
    """
    Запросы для проверки состояния сервиса
    """

    def __init__(
        self,
        booking_payments_maintenance_repo: Type[BookingPaymentsMaintenanceRepo],
        client_check_maintenance_repo: Type[ClientCheckMaintenanceRepo],
        client_assign_maintenance_repo: Type[ClientAssignMaintenanceRepo],
    ):
        self.booking_payments_maintenance_repo = booking_payments_maintenance_repo()
        self.client_check_maintenance_repo = client_check_maintenance_repo()
        self.client_assign_maintenance_repo = client_assign_maintenance_repo()

    async def get_successful_payments_count(self) -> int:
        return await self.booking_payments_maintenance_repo.count(
            filters=dict(successful_payment=True, created_at__gt=datetime.now() - timedelta(hours=1)),
        )

    async def get_unsuccessful_payments_count(self) -> int:
        return await self.booking_payments_maintenance_repo.count(
            filters=dict(successful_payment=False, created_at__gt=datetime.now() - timedelta(hours=1)),
        )

    async def get_successful_check_count(self) -> int:
        return await self.client_check_maintenance_repo.count(
            filters=dict(successful_check=True, created_at__gt=datetime.now() - timedelta(hours=1)),
        )

    async def get_successful_assign_count(self) -> int:
        return await self.client_assign_maintenance_repo.count(
            filters=dict(successful_assign=True, created_at__gt=datetime.now() - timedelta(hours=1)),
        )

    async def get_unsuccessful_check_count(self) -> int:
        return await self.client_check_maintenance_repo.count(
            filters=dict(successful_check=False, created_at__gt=datetime.now() - timedelta(hours=1)),
        )

    async def get_unsuccessful_assign_count(self) -> int:
        return await self.client_assign_maintenance_repo.count(
            filters=dict(successful_assign=False, created_at__gt=datetime.now() - timedelta(hours=1)),
        )
