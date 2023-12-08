from tortoise import Model, fields

from common.orm.entities import BaseRepo
from common.orm.mixins import CRUDMixin


class MortgageForm(Model):
    """
    Форма ик.
    """
    id: int = fields.IntField(description="ID", pk=True)
    phone: str = fields.CharField(
        max_length=20, description="Номер телефона"
    )
    surname: str = fields.CharField(
        max_length=100, description="Фамилия"
    )
    name: str = fields.CharField(
        max_length=100, description="Имя"
    )
    patronymic: str = fields.CharField(
        max_length=100, description="Отчество"
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        table = "mortgage_form"


class MortgageFormRepo(BaseRepo, CRUDMixin):
    """
    Репозиторий форм ик.
    """
    model = MortgageForm
