from datetime import datetime
from typing import TYPE_CHECKING, TypedDict, Optional

from tortoise import fields, Model
from tortoise.fields import ForeignKeyRelation

from ..constants import OnlinePurchaseSteps
from ..entities import BaseBookingRepo


if TYPE_CHECKING:
    from src.users.repos.user import User
    from src.properties.repos.property import Property
    from .booking import Booking


class BookingHistoryDocument(TypedDict):
    name: str
    size: int
    url: str


class BookingHistory(Model):
    """
    Конкретная запись из истории сделки
    """

    id: int = fields.IntField(description="ID", pk=True)
    booking: ForeignKeyRelation["Booking"] = fields.ForeignKeyField(
        description="Сделка", model_name="models.Booking", related_name=False
    )
    # Необходимо для высчитывания того, нужно ли отображать кнопку "Продолжить", или нет
    created_at_online_purchase_step: str = fields.CharField(
        max_length=32, description="Стадия онлайн-покупки сделки на момент создания записи"
    )
    property: ForeignKeyRelation["Property"] = fields.ForeignKeyField(
        description="Собственность", model_name="models.Property", related_name=False
    )
    documents: list[list[BookingHistoryDocument]] = fields.JSONField(
        description="Прикреплённые документы", default=[]
    )
    created_at: datetime = fields.DatetimeField(
        description="Дата и время создания", auto_now_add=True
    )

    message: str = fields.CharField(max_length=1000, description="Описание")

    # Денормализовано для быстрой фильтрации
    user: ForeignKeyRelation["User"] = fields.ForeignKeyField(
        description="Сделка", model_name="models.User", related_name=False
    )

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        table = "booking_history"


class BookingHistoryRepo(BaseBookingRepo):
    """
    Репозиторий истории сделок пользователя
    """

    async def create(
        self,
        *,
        booking: "Booking",
        previous_online_purchase_step: str,
        message: str,
        documents: Optional[list[list[BookingHistoryDocument]]] = None
    ) -> BookingHistory:
        """
        Создание записи в истории сделок пользователя
        """
        if previous_online_purchase_step is None:
            raise ValueError("BookingHistoryRepo: create: Стадия онлайн-покупки сделки = None!")
        return await BookingHistory.create(
            user_id=booking.user_id,
            booking=booking,
            property_id=booking.property_id,
            message=message,
            created_at_online_purchase_step=previous_online_purchase_step,
            documents=documents if documents is not None else [],
        )

    async def list(
        self, *, user_id: int, limit: int, offset: int
    ) -> tuple[list[BookingHistory], bool]:
        """
        Истории сделок конкретного пользователя
        """
        booking_history = await (
            BookingHistory.all()
            .filter(user_id=user_id)
            .limit(limit + 1)
            .offset(offset)
            .order_by("-created_at")
            .select_related("property", "user")
        )
        next_page = len(booking_history) > limit
        return booking_history[:limit], next_page
