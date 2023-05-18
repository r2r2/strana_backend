from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from pydantic import validator
from tortoise import fields, Model
from tortoise.fields import ForeignKeyRelation

from src.booking.constants import OnlinePurchaseSteps
from ..entities import BaseNotificationRepo, BaseNotificationModel

if TYPE_CHECKING:
    from src.users.repos.user import User
    from src.properties.repos.property import Property
    from src.booking.repos.booking import Booking


class ClientNotification(Model):
    """
    Уведомление клиента
    """

    id: int = fields.IntField(description="ID", pk=True)
    title: str = fields.CharField(max_length=250)
    description: str = fields.CharField(max_length=1000)
    is_new: bool = fields.BooleanField(
        description="Прочитано пользователем", index=True, default=True
    )
    booking: ForeignKeyRelation["Booking"] = fields.ForeignKeyField(
        description="Сделка", model_name="models.Booking", related_name=False
    )
    # Нужно для высчитывания того, можно ли показывать пользователю кнопку "Продолжить" или же
    created_at_online_purchase_step: str = fields.CharField(
        max_length=32, description="Стадия онлайн-покупки сделки на момент создания записи"
    )
    moved_to_online_purchase_step: str = fields.CharField(
        max_length=32, description="Стадия онлайн-покупки, на которую перешла сделка"
    )
    property: ForeignKeyRelation["Property"] = fields.ForeignKeyField(
        description="Собственность", model_name="models.Property", related_name=False
    )
    created_at: datetime = fields.DatetimeField(
        description="Дата и время создания", auto_now_add=True
    )

    # Денормализовано для быстрой фильтрации
    user: ForeignKeyRelation["User"] = fields.ForeignKeyField(
        description="Сделка", model_name="models.User", related_name=False
    )

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        table = "notifications_clients"

    class PydanticMeta:
        exclude = (
            "booking",
            "property",
            "user",
        )


class BookingModel(BaseNotificationModel):
    id: int
    online_purchase_step: str

    @validator("online_purchase_step", pre=True, always=True)
    def get_online_purchase_step(cls, online_purchase_step) -> str:
        if online_purchase_step is None or isinstance(online_purchase_step, str):
            return online_purchase_step
        return online_purchase_step()

    class Config:
        orm_mode = True


class PropertyModel(BaseNotificationModel):
    area: Optional[Decimal]
    rooms: Optional[int]

    class Config:
        orm_mode = True


class ClientNotificationSchema(BaseNotificationModel):
    id: int
    booking: BookingModel
    title: str
    description: str
    property: PropertyModel
    created_at: datetime
    is_new: bool
    show_download_button: bool
    show_continue_button: bool


class IsNewModel(BaseNotificationModel):
    label: str
    value: bool
    exists: bool


class ClientNotificationSpecsSchema(BaseNotificationModel):
    is_new: list[IsNewModel]


class ClientNotificationFacetsSchema(BaseNotificationModel):
    is_new: list[bool]


class ClientNotificationRepo(BaseNotificationRepo):
    """
    Репозиторий оповещений по сделкам пользователя
    """

    async def create(
        self,
        *,
        booking: "Booking",
        title: str,
        description: str,
        created_at_online_purchase_step: OnlinePurchaseSteps
    ) -> ClientNotification:
        """
        Создание оповещения
        """
        online_purchase_step = booking.online_purchase_step()
        if online_purchase_step is None:
            raise ValueError("BookingHistoryRepo: create: Стадия онлайн-покупки сделки = None!")
        return await ClientNotification.create(
            user_id=booking.user_id,
            booking=booking,
            title=title,
            description=description,
            property_id=booking.property_id,
            created_at_online_purchase_step=created_at_online_purchase_step,
            moved_to_online_purchase_step=online_purchase_step,
        )

    async def set_new(self, *, is_new: bool, user_id: int, ids: list[int]) -> None:
        """
        Отметка оповещений, как прочитанных.
        """
        await ClientNotification.all().filter(user_id=user_id, id__in=ids).update(is_new=is_new)

    async def list(
        self, *, user_id: int, limit: int, offset: int
    ) -> tuple[list[ClientNotificationSchema], bool]:
        """
        Список оповещений
        """
        query = (
            ClientNotification.all().filter(user_id=user_id).select_related("booking", "property")
        )

        query = query.limit(limit + 1).offset(offset).order_by("-created_at")

        booking_notifications = await query

        next_page = len(booking_notifications) > limit
        return [
            ClientNotificationSchema(
                id=notification.id,
                booking=BookingModel(
                    id=notification.booking_id,
                    online_purchase_step=notification.created_at_online_purchase_step,
                ),
                title=notification.title,
                description=notification.description,
                property=PropertyModel.from_orm(notification.property),
                created_at=notification.created_at,
                is_new=notification.is_new,
                show_download_button=(
                    notification.moved_to_online_purchase_step == OnlinePurchaseSteps.FINISHED
                ),
                show_continue_button=(
                    notification.moved_to_online_purchase_step
                    == notification.booking.online_purchase_step()
                ),
            )
            for notification in booking_notifications[:limit]
        ], next_page

    async def specs(self, *, user_id: int) -> ClientNotificationSpecsSchema:
        """
        Спеки оповещений
        """
        is_new_specs = [
            {"label": "Новые", "value": True, "exists": False},
            {"label": "Просмотренные", "value": False, "exists": False},
        ]
        query = (
            ClientNotification.all()
            .filter(user_id=user_id)
            .group_by("is_new")
            .values_list("is_new", flat=True)
        )
        is_new_choices = await query

        if True in is_new_choices:
            is_new_specs[0]["exists"] = True
        if False in is_new_choices:
            is_new_specs[1]["exists"] = True

        return ClientNotificationSpecsSchema(is_new=is_new_specs)

    async def facets(self, *, user_id: int) -> ClientNotificationFacetsSchema:
        """
        Фасеты оповещений
        """
        query = (
            ClientNotification.all()
            .filter(user_id=user_id)
            .group_by("is_new")
            .values_list("is_new", flat=True)
        )
        is_new_facets = await query
        return ClientNotificationFacetsSchema(is_new=is_new_facets)
