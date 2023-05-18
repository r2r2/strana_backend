from decimal import Decimal
from typing import Optional

from common.orm.mixins import (DeleteMixin, ListMixin, ReadWriteMixin,
                               RetrieveMixin, UpdateOrCreateMixin)
from src.projects.repos import Project
from tortoise import Model, fields

from ..entities import BaseBuildingRepo


class BuildingBookingType(Model):
    """
    Тип бронирования у корпусов.

    Здесь указывается срок бронирования и цена, чтобы можно было выбрать вариант подешевле, но на
    короткий срок бронирования, а также подороже, но подольше.
    """

    # Тянем записи с бэкенда, поэтому не автоинкремент
    id: int = fields.IntField(description="ID", pk=True)

    period: int = fields.IntField(verbose_name="Длительность бронирования")
    price: int = fields.IntField(verbose_name="Стоимость бронирования")
    amocrm_id: Optional[int] = fields.BigIntField(description="Идентификатор АМОЦРМ", null=True)

    def __str__(self) -> str:
        return f"Длительность: {self.period}, стоимость: {self.price}"

    class Meta:
        table = "buildings_building_booking_type"


class Building(Model):
    """
    Корпус
    """

    id: int = fields.IntField(description="ID", pk=True)
    address: Optional[str] = fields.CharField(description="Адресс", max_length=300, null=True)
    global_id: Optional[str] = fields.CharField(
        description="Глобальный ID", max_length=200, unique=True, null=True
    )
    name: Optional[str] = fields.CharField(description="Имя", max_length=100, null=True)
    built_year: Optional[int] = fields.IntField(description="Год постройки", null=True)
    ready_quarter: Optional[int] = fields.IntField(description="Квартал готовности", null=True)
    total_floor: Optional[int] = fields.IntField(description="Этажей", null=True)
    booking_active: bool = fields.BooleanField(description="Бронирование активно", default=True)
    booking_period: Optional[int] = fields.IntField(description="Период бронирования", null=True)
    booking_price: Optional[int] = fields.IntField(description="Стоимость бронирования", null=True)
    project: fields.ForeignKeyNullableRelation[Project] = fields.ForeignKeyField(
        description="Проект", model_name="models.Project", related_name="buildings", null=True
    )
    default_commission: Optional[Decimal] = fields.DecimalField(
        description="Коммиссия (по умолчанию)", decimal_places=2, max_digits=5, null=True, default=1
    )
    booking_types: fields.ManyToManyRelation[BuildingBookingType] = fields.ManyToManyField(
        model_name="models.BuildingBookingType",
        related_name="buildings",
        through="building_building_booking_type_m2m",
    )

    def __str__(self) -> str:
        if self.name:
            return self.name
        return str(self.id)

    class Meta:
        table = "buildings_building"


class BuildingBookingTypeRepo(BaseBuildingRepo, UpdateOrCreateMixin, ListMixin, RetrieveMixin, DeleteMixin):
    """
    Репозиторий типов бронирования
    """
    model = BuildingBookingType


class BuildingRepo(BaseBuildingRepo, ReadWriteMixin):
    """
    Репозиторий корпуса
    """
    model = Building
