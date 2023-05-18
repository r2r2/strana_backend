from tortoise import Model, fields

from common.orm.mixins import CRUDMixin
from ..entities import BaseTemplateRepo


class ActTemplate(Model):
    """
    Репозиторий шаблонов актов
    """

    id: int = fields.IntField(description="ID", pk=True, index=True)
    template_name: str = fields.CharField(description='Название шаблона', max_length=150)
    project: fields.ForeignKeyNullableRelation["Project"] = fields.ForeignKeyField(
        model_name="models.Project",
        on_delete=fields.CASCADE,
        related_name="acts",
        description="Проект"
    )

    def __str__(self) -> str:
        return self.template_name

    class Meta:
        table = "acts_templates"


class ActTemplateRepo(BaseTemplateRepo, CRUDMixin):
    """
    Репозиторий актов
    """
    model = ActTemplate
