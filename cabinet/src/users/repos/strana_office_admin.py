from tortoise import Model, fields

from common import cfields
from ..entities import BaseUserRepo
from common.orm.mixins import ReadOnlyMixin
from ...meetings.constants import MeetingType


class StranaOfficeAdmin(Model):
    """
    Администратор офиса "Страна"
    """

    id: int = fields.IntField(description="ID", pk=True, index=True)
    fio: str = fields.CharField(description="ФИО админа", max_length=100)
    projects: fields.ManyToManyRelation = fields.ManyToManyField(
        model_name="models.Project",
        related_name="project_admin",
        on_delete=fields.CASCADE,
        description="Проекты",
        through="users_strana_office_admins_project_through",
        backward_key="strana_office_admin_id",
        forward_key="project_id",
    )
    email: str = fields.CharField(
        description="Email", max_length=100
    )
    type: str = cfields.CharChoiceField(
        max_length=20, choice_class=MeetingType, default=MeetingType.ONLINE, description="Тип встречи"
    )

    class Meta:
        table = "users_strana_office_admin"


class StranaOfficeAdminsProjectsThrough(Model):
    """
    Проекты админов
    """

    strana_office_admin: fields.ForeignKeyRelation[StranaOfficeAdmin] = fields.ForeignKeyField(
        model_name="models.StranaOfficeAdmin",
        related_name="strana_office_admin_project_through",
        description="Админ",
        on_delete=fields.CASCADE,
    )
    project: fields.ForeignKeyRelation["Project"] = fields.ForeignKeyField(
        model_name="models.Project",
        related_name="project_strana_office_admin_through",
        description="Проекты",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "users_strana_office_admins_project_through"


class StranaOfficeAdminRepo(BaseUserRepo, ReadOnlyMixin):
    """
    Репозиторий администратор офиса "Страна"
    """
    model = StranaOfficeAdmin
