from datetime import datetime

from tortoise import Model, fields
from tortoise.fields import ForeignKeyNullableRelation

from common import orm
from common.orm.mixins import CRUDMixin
from src.agencies.repos import Agency
from src.projects.repos import Project
from src.users.entities import BaseUserRepo
from src.users.repos.user import User


class Check(Model):
    """
    Проверка
    """

    id: int = fields.BigIntField(description="ID", pk=True)
    requested: datetime | None = fields.DatetimeField(
        description="Запрошено", null=True
    )
    dispute_requested: datetime | None = fields.DatetimeField(
        description="Время оспаривания", null=True
    )
    status_fixed: bool = fields.BooleanField(
        description="Закрепить статус за клиентом", default=False
    )
    unique_status: fields.ForeignKeyNullableRelation[
        "UniqueStatus"
    ] = fields.ForeignKeyField(
        description="Статус уникальности",
        model_name="models.UniqueStatus",
        on_delete=fields.CASCADE,
        related_name="checks",
        null=True,
    )
    user: ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        description="Пользователь",
        model_name="models.User",
        on_delete=fields.SET_NULL,
        related_name="users_checks",
        null=True,
    )
    agent: ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        description="Агент",
        model_name="models.User",
        on_delete=fields.SET_NULL,
        related_name="agents_checks",
        null=True,
    )
    dispute_agent: ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        description="Оспаривающий агент",
        model_name="models.User",
        on_delete=fields.SET_NULL,
        related_name="dispute_agents_checks",
        null=True,
    )
    agency: ForeignKeyNullableRelation[Agency] = fields.ForeignKeyField(
        description="Агентство",
        model_name="models.Agency",
        on_delete=fields.SET_NULL,
        related_name="agencies_checks",
        null=True,
    )
    admin: ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        description="Админ",
        model_name="models.User",
        on_delete=fields.SET_NULL,
        related_name="admin_checks",
        null=True,
    )
    django_admin_email: str | None = fields.CharField(
        description="Email", max_length=100, null=True
    )
    comment: str | None = fields.TextField(description="Комментарий агента", null=True)
    admin_comment: str | None = fields.TextField(
        description="Комментарий менеджера", null=True
    )
    send_admin_email: bool = fields.BooleanField(
        default=False,
        description="Отправлено письмо администраторам",
    )
    send_rop_email: bool = fields.BooleanField(
        default=False,
        description="Отправлено письмо РОПам",
    )
    amocrm_id: int | None = fields.IntField(
        description="ID сделки в amoCRM, по которой была проверка", null=True
    )
    project: fields.ForeignKeyRelation[Project] = fields.ForeignKeyField(
        model_name="models.Project", description='Проект', on_delete=fields.CASCADE, null=True,
    )
    term_uid: str | None = fields.CharField(
        description="UID условия проверки на уникальность",
        max_length=255,
        null=True,
    )
    term_comment: str | None = fields.TextField(
        description="Комментарий к условию проверки на уникальность",
        null=True,
    )
    button_slug: str | None = fields.CharField(
        description="Слаг кнопки",
        max_length=255,
        null=True,
    )

    button_pressed: bool = fields.BooleanField(
        description="Кнопка была нажата", default=False
    )
    dispute_status: fields.ForeignKeyNullableRelation[
        "UniqueStatus"
    ] = fields.ForeignKeyField(
        model_name="models.DisputeStatus",
        related_name="dispute_status",
        description="Статус оспаривания",
        null=True,
    )
    agent_id: int | None
    dispute_agent_id: int | None

    class Meta:
        table = "users_checks"


class CheckRepo(BaseUserRepo, CRUDMixin):
    """
    Репозиторий проверки
    """

    model = Check
    q_builder: orm.QBuilder = orm.QBuilder(Check)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(Check)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(Check)
