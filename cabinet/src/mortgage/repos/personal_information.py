from datetime import datetime

from pytz import UTC
from tortoise import Model, fields

from common.orm.mixins import CRUDMixin
from src.mortgage.entities import BaseMortgageRepo


class PersonalInformation(Model):
    """
    Форма ипотечного калькулятора.
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
        max_length=100, description="Отчество", null=True
    )
    position: str = fields.CharField(
        max_length=100,
        description="Должность",
        null=True,
    )
    company: str = fields.CharField(
        max_length=100,
        description="Компания",
        null=True,
    )
    experience: str = fields.CharField(
        max_length=100,
        description="Стаж работы",
        null=True,
    )
    average_salary: str = fields.CharField(
        max_length=100,
        description="Средняя зарплата",
        null=True,
    )
    document_id: int = fields.IntField(
        description="ID документа",
        null=True,
    )
    booking: fields.ForeignKeyRelation["Booking"] = fields.ForeignKeyField(
        model_name="models.Booking",
        related_name="mortgage_forms",
        description="Бронь",
        null=True,
        on_delete=fields.CASCADE,
    )
    created_at: datetime = fields.DatetimeField(
        description="Дата создания",
        auto_now_add=True,
        default=datetime.now(tz=UTC),
    )
    updated_at: datetime = fields.DatetimeField(
        description="Дата обновления",
        auto_now=True,
        default=datetime.now(tz=UTC),
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        table = "personal_information"


class PersonalInformationRepo(BaseMortgageRepo, CRUDMixin):
    """
    Репозиторий форм ик.
    """
    model = PersonalInformation
