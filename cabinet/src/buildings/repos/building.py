from decimal import Decimal

from tortoise import Model, fields

from common import orm, cfields
from common.orm.mixins import (
    DeleteMixin,
    ListMixin,
    ReadWriteMixin,
    RetrieveMixin,
    UpdateOrCreateMixin,
)
from src.projects.repos import Project
from ..entities import BaseBuildingRepo
from ..constants import BuildingType


class BuildingBookingType(Model):
    """
    Тип бронирования у корпусов.

    Здесь указывается срок бронирования и цена, чтобы можно было выбрать вариант подешевле, но на
    короткий срок бронирования, а также подороже, но подольше.
    """

    # Тянем записи с бэкенда, поэтому не автоинкремент
    id: int = fields.IntField(description="ID", pk=True)

    period: int = fields.IntField(description="Длительность бронирования")
    price: int = fields.IntField(description="Стоимость бронирования")
    amocrm_id: int | None = fields.BigIntField(
        description="Идентификатор АМОЦРМ", null=True
    )
    priority: int | None = fields.IntField(
        description="Приоритет вывода (чем меньше чем, тем раньше)", null=True
    )

    def __str__(self) -> str:
        return f"Длительность: {self.period}, стоимость: {self.price}"

    class Meta:
        table = "buildings_building_booking_type"


class Building(Model):
    """
    Корпус
    """

    id: int = fields.IntField(description="ID", pk=True)
    address: str | None = fields.CharField(
        description="Адресс", max_length=300, null=True
    )
    global_id: str | None = fields.CharField(
        description="Глобальный ID", max_length=200, unique=True, null=True
    )
    name: str | None = fields.CharField(description="Имя", max_length=100, null=True)
    name_display = fields.CharField(
        description="Отображаемое имя", max_length=100, null=True
    )
    built_year: int | None = fields.IntField(description="Год постройки", null=True)
    ready_quarter: int | None = fields.IntField(
        description="Квартал готовности", null=True
    )
    total_floor: int | None = fields.IntField(description="Этажей", null=True)
    booking_active: bool = fields.BooleanField(
        description="Бронирование активно", default=True
    )
    booking_period: int | None = fields.IntField(
        description="Период бронирования", null=True
    )
    booking_price: int | None = fields.IntField(
        description="Стоимость бронирования", null=True
    )
    project: fields.ForeignKeyNullableRelation[Project] = fields.ForeignKeyField(
        description="Проект",
        model_name="models.Project",
        related_name="buildings",
        null=True,
    )
    default_commission: Decimal | None = fields.DecimalField(
        description="Коммиссия (по умолчанию)",
        decimal_places=2,
        max_digits=5,
        null=True,
        default=1,
    )
    booking_types: fields.ManyToManyRelation[
        BuildingBookingType
    ] = fields.ManyToManyField(
        model_name="models.BuildingBookingType",
        related_name="buildings",
        through="building_building_booking_type_m2m",
    )
    kind: str = cfields.CharChoiceField(
        description="Тип строения",
        default=BuildingType.RESIDENTIAL,
        choice_class=BuildingType,
        max_length=32,
    )
    flats_0_min_price = fields.DecimalField(
        description="Мин цена студия", max_digits=14, decimal_places=2, null=True
    )
    flats_1_min_price = fields.DecimalField(
        description="Мин цена 1-комн", max_digits=14, decimal_places=2, null=True
    )
    flats_2_min_price = fields.DecimalField(
        description="Мин цена 2-комн", max_digits=14, decimal_places=2, null=True
    )
    flats_3_min_price = fields.DecimalField(
        description="Мин цена 3-комн", max_digits=14, decimal_places=2, null=True
    )
    flats_4_min_price = fields.DecimalField(
        description="Мин цена 4-комн", max_digits=14, decimal_places=2, null=True
    )
    show_in_paid_booking: bool = fields.BooleanField(
        description="Отображать в платном бронировании", default=True
    )
    discount: int = fields.SmallIntField(description="Скидка в %", default=0)

    def __str__(self) -> str:
        if self.name:
            return self.name
        return str(self.id)

    class Meta:
        table = "buildings_building"


class BuildingBookingTypeRepo(
    BaseBuildingRepo, UpdateOrCreateMixin, ListMixin, RetrieveMixin, DeleteMixin
):
    """
    Репозиторий типов бронирования
    """

    model = BuildingBookingType


class BuildingRepo(BaseBuildingRepo, ReadWriteMixin):
    """
    Репозиторий корпуса
    """

    model = Building
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(Building)
