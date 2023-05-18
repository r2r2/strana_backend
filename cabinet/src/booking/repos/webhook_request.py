from datetime import datetime

from tortoise import Model, fields

from common import orm
from common.orm.mixins import CRUDMixin, SCountMixin

from ..entities import BaseBookingRepo


class WebhookRequest(Model):
    """
    Webhook запрос.

    Задумывался как архив всех запросов.
    """

    id: int = fields.IntField(description="ID", pk=True)
    category: str = fields.CharField(description="Тип вебхука", max_length=20)
    body: str = fields.TextField(description="Тело запроса")
    created_at: datetime = fields.DatetimeField(description="Дата создания", auto_now_add=True)

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        table = "booking_webhook_request"


class WebhookRequestRepo(BaseBookingRepo, CRUDMixin, SCountMixin):
    """
    Репозиторий webhook запросов
    """

    model = WebhookRequest
    q_builder: orm.QBuilder = orm.QBuilder(WebhookRequest)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(WebhookRequest)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(WebhookRequest)
