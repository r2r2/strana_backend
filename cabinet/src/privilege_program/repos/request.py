from datetime import datetime

from common.orm.mixins import ReadWriteMixin
from tortoise import Model, fields

from ..entities import BasePrivilegeRepo


class PrivilegeRequest(Model):
    """
    Запрос в Программу привилегий
    """
    id: int = fields.IntField(pk=True, description="ID")
    user = fields.ForeignKeyField(
        description="Пользователь",
        model_name="models.User",
        related_name="privilege_requests",
        null=True,
    )
    full_name: str = fields.CharField(max_length=150, description="ФИО клиента")
    phone: str = fields.CharField(
        max_length=20, description="Номер телефона", index=True
    )
    email: str = fields.CharField(description="Email", max_length=100)
    question: str = fields.TextField(description="Вопрос")

    created_at = fields.DatetimeField(auto_now_add=True, description="Время создания")
    updated_at = fields.DatetimeField(auto_now=True, description="Время последнего обновления")

    class Meta:
        table = "privilege_request"

    def __repr__(self):
        return self.full_name


class PrivilegeRequestRepo(BasePrivilegeRepo, ReadWriteMixin):
    """
    Репозиторий Программ привилегий
    """
    model = PrivilegeRequest
