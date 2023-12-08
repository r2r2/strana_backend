from tortoise import Model, fields

from ..entities import BaseUserRepo
from common.orm.mixins import ReadOnlyMixin


class StranaOfficeAdmin(Model):
    """
    Администратор офиса "Страна"
    """

    id: int = fields.IntField(description="ID", pk=True, index=True)
    fio: str = fields.CharField(description="ФИО админа", max_length=100)
    project: fields.ForeignKeyRelation = fields.ForeignKeyField(
        description="Проект",
        model_name="models.Project",
        related_name="project_admin",
        on_delete=fields.CASCADE,
    )
    email: str = fields.CharField(
        description="Email", max_length=100
    )

    class Meta:
        table = "users_strana_office_admin"


class StranaOfficeAdminRepo(BaseUserRepo, ReadOnlyMixin):
    """
    Репозиторий администратор офиса "Страна"
    """
    model = StranaOfficeAdmin
