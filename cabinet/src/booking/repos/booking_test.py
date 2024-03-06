"""
Test Booking repo
"""

from datetime import datetime
from typing import Any

from tortoise import Model, fields
from tortoise.fields import ForeignKeyNullableRelation

from common import cfields
from common.orm.mixins import CRUDMixin
from config import maintenance_settings, EnvTypes
from . import Booking
from ..constants import TestBookingStatuses
from ..entities import BaseBookingRepo


class TestBooking(Model):
    """
    Тестовое Бронирование
    """

    statuses = TestBookingStatuses()

    id: int = fields.IntField(description="ID", pk=True)
    booking: ForeignKeyNullableRelation[Booking] = fields.ForeignKeyField(
        description="Бронирование",
        model_name="models.Booking",
        on_delete=fields.SET_NULL,
        related_name="booking_test",
        null=True,
        index=True,
    )
    amocrm_id: str = fields.CharField(description="AMOCRM ID", max_length=50, index=True)
    status: str = cfields.CharChoiceField(
        description="Статус",
        max_length=20,
        default=TestBookingStatuses.IN_AMO,
        choice_class=TestBookingStatuses,
        null=True,
        index=True,
    )

    info: str = fields.TextField(description="Примечание", null=True)
    last_check_at: datetime = fields.DatetimeField(description="Дата последней проверки", null=True)
    is_check_skipped: bool = fields.BooleanField(description="Исключить из проверки", default=False)
    created_at: datetime = fields.DatetimeField(description="Дата создания", auto_now_add=True)
    updated_at: datetime = fields.DatetimeField(auto_now=True, description='Дата обновления')

    def __str__(self):
        return f"<{self.id}>"

    class Meta:
        table = "booking_testbooking"


class TestBookingRepo(BaseBookingRepo, CRUDMixin):
    """
    Репозиторий тестового бронирования
    """

    model = TestBooking

    async def create(self, data: dict[str, Any]) -> TestBooking | None:
        """
        Создание
        """
        if maintenance_settings["environment"] == EnvTypes.DEV:
            data["info"] = "dev"
            return await self.model.create(**data)

        elif maintenance_settings["environment"] == EnvTypes.STAGE:
            data["info"] = "stage"
            return await self.model.create(**data)

        elif data['is_test_user']:
            data["info"] = "prod"
            return await self.model.create(**data)
