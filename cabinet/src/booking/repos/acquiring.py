from tortoise import Model, fields

from common.models import TimeBasedMixin
from common.orm.entities import BaseRepo
from common.orm.mixins import CRUDMixin


class Acquiring(Model, TimeBasedMixin):
    """
    Эквайринги
    """

    id: int = fields.IntField(description="ID", pk=True)
    city: fields.ForeignKeyRelation["City"] = fields.ForeignKeyField(
        model_name="models.City",
        related_name="acquiring",
        description="Город",
        null=False,
    )
    is_active: bool = fields.BooleanField(description="Активный", default=False)
    username: str = fields.CharField(description="Имя пользователя", max_length=100, null=False)
    password: str = fields.CharField(description="Пароль", max_length=200, null=False)

    class Meta:
        table = "booking_acquiring"
        unique_together = (('city', 'is_active'),)

    def __str__(self) -> str:
        return str(self.city.name)


class AcquiringRepo(BaseRepo, CRUDMixin):
    """
    Репозиторий эквайринга
    """
    model = Acquiring
