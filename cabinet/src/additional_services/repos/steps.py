from tortoise import fields

from common.orm.mixins import ReadWriteMixin
from ..entities import BaseAdditionalServiceDatabaseModel, BaseAdditionalServiceRepo


class AdditionalServiceConditionStep(BaseAdditionalServiceDatabaseModel):
    """
    Шаг для "Как получить услугу"
    """

    id: int = fields.IntField(description="ID", pk=True)
    priority: int = fields.IntField(default=0, description="Приоритет")
    description: str = fields.TextField(description="Текст описания")
    active: bool = fields.BooleanField(description="Активность", default=True)
    condition: fields.ForeignKeyRelation[
        "AdditionalServiceCondition"
    ] = fields.ForeignKeyField(
        model_name="models.AdditionalServiceCondition",
        related_name="condition_steps",
        null=True,
        on_delete=fields.SET_NULL,
    )

    class Meta:
        table = "additional_services_condition_step"


class AdditionalServiceConditionStepRepo(BaseAdditionalServiceRepo, ReadWriteMixin):
    """
    Репозиторий шага для "Как получить услугу"
    """

    model = AdditionalServiceConditionStep
