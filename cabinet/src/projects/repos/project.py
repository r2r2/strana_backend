from typing import Any, Optional

from tortoise import Model, fields
from tortoise.fields import ForeignKeyNullableRelation

from common import cfields, orm
from common.orm.mixins import CountMixin, CRUDMixin, FacetsMixin
from ..entities import BaseProjectRepo
from ..constants import ProjectStatus


class Project(Model):
    """
    Проект
    """

    id: int = fields.IntField(description="ID", pk=True)
    slug: Optional[str] = fields.CharField(description="Слаг", max_length=100, null=True)
    global_id: Optional[str] = fields.CharField(
        description="Глобальный ID", max_length=200, unique=True, null=True
    )
    name: Optional[str] = fields.CharField(description="Имя", max_length=200, null=True)
    city: ForeignKeyNullableRelation["City"] = fields.ForeignKeyField(
        "models.City", related_name="projects", null=True, on_delete=fields.SET_NULL,
    )
    amocrm_name: Optional[str] = fields.CharField(
        description="Имя AmoCRM", max_length=200, null=True
    )
    amocrm_enum: Optional[int] = fields.BigIntField(description="Enum в AmoCRM", null=True)
    amocrm_organization: Optional[str] = fields.CharField(
        description="Организация в AmoCRM", max_length=200, null=True
    )
    amo_pipeline_id: Optional[str] = fields.CharField(
        description="ID воронки в AmoCRM", max_length=200, null=True
    )
    amo_responsible_user_id: Optional[str] = fields.CharField(
        description="ID ответственного в AmoCRM", max_length=200, null=True
    )
    is_active: bool = fields.BooleanField(description="Активный", default=True)
    priority: int = fields.IntField(description="Приоритет вывода", null=True)
    status: str = cfields.CharChoiceField(
        description="Статус", max_length=200, default=ProjectStatus.CURRENT, choice_class=ProjectStatus
    )

    def __str__(self) -> str:
        if self.name:
            return self.name
        return str(self.id)

    class Meta:
        table = "projects_project"
        ordering = ["priority"]


class ProjectRepo(BaseProjectRepo, CRUDMixin, CountMixin, FacetsMixin):
    """
    Репозиторий проекта
    """
    model = Project
    q_builder: orm.QBuilder = orm.QBuilder(Project)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(Project)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(Project)

    async def update_or_create(self, filters: dict[str, Any], data: dict[str, Any]) -> Project:
        """
        Создание или обновление проекта
        """
        if not data.get('amocrm_enum'):
            data['amocrm_enum'] = 0
        project, _ = await Project.update_or_create(**filters, defaults=data)
        return project
