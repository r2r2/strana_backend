from tortoise import Model, fields
from tortoise.fields import ForeignKeyRelation

from common.models import TimeBasedMixin
from common.orm.mixins import CRUDMixin
from src.notifications.entities import BaseNotificationRepo


class AssignClientTemplate(Model, TimeBasedMixin):
    """
    Шаблон сообщений для закрепления клиента
    """
    id: int = fields.IntField(description="ID", pk=True)
    title: str = fields.CharField(max_length=255, description="Название")
    text: str = fields.TextField(description="Текст открепления")
    success_assign_text: str = fields.TextField(description="Текст страницы успешного закрепления", null=True)
    success_unassign_text: str = fields.TextField(description="Текст страницы успешного открепления", null=True)
    default: bool = fields.BooleanField(description="По умолчанию", default=False)
    is_active: bool = fields.BooleanField(description="Активен", default=True)
    city: ForeignKeyRelation["City"] = fields.ForeignKeyField(
        model_name="models.City",
        related_name="assign_clients",
        on_delete=fields.CASCADE,
    )
    sms: ForeignKeyRelation["SmsTemplate"] = fields.ForeignKeyField(
        model_name="models.SmsTemplate",
        related_name="assign_clients",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "notifications_assignclient"


class AssignClientTemplateRepo(BaseNotificationRepo, CRUDMixin):
    model = AssignClientTemplate
