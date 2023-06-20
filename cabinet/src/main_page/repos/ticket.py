from typing import Optional

from tortoise import Model, fields

from common.orm.mixins import CRUDMixin
from src.main_page.entities import BaseMainPageRepo


class Ticket(Model):
    """
    Заявка
    """
    name: str = fields.CharField(max_length=255)
    phone: Optional[str] = fields.CharField(description="Номер телефона", max_length=20)
    user_amocrm_id: Optional[int] = fields.IntField(description="ID пользователя в AmoCRM", null=True)
    booking_amocrm_id: Optional[int] = fields.IntField(description="ID брони в AmoCRM", null=True)
    note: Optional[str] = fields.TextField(description="Примечание", null=True)
    type: str = fields.CharField(max_length=255)
    city: fields.ManyToManyRelation["City"] = fields.ManyToManyField(
        model_name="models.City",
        related_name="tickets",
        on_delete=fields.CASCADE,
        description="Город",
        through="mainpage_ticket_city_through",
        backward_key="ticket_id",
        forward_key="city_id",
    )
    created_at = fields.DatetimeField(auto_now_add=True, description="Время создания")
    updated_at = fields.DatetimeField(auto_now=True, description="Время последнего обновления")

    def __str__(self) -> str:
        return self.name

    class Meta:
        table = "mainpage_ticket"


class TicketRepo(BaseMainPageRepo, CRUDMixin):
    """
    Репозиторий заявки
    """
    model = Ticket
