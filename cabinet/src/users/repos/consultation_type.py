from tortoise import Model, fields

from common.orm.mixins import ReadOnlyMixin
from ..entities import BaseUserRepo


class ConsultationType(Model):
    """
    Справочник типов консультаций
    """
    id: int = fields.IntField(description="ID", pk=True, index=True)
    name: str = fields.CharField(description="Название", max_length=30)
    slug: str = fields.CharField(description="Слаг", max_length=30, unique=True)
    priority: str = fields.IntField(description="Приоритет", default=0)

    fixing_conditions: fields.ReverseRelation["BookingFixingConditionsMatrix"]

    def __str__(self) -> str:
        return self.name

    class Meta:
        table = "users_consultation_type"
        ordering = ['priority']


class ConsultationTypeRepo(BaseUserRepo, ReadOnlyMixin):
    """
    Репозиторий справочника типов консультаций
    """
    model = ConsultationType
