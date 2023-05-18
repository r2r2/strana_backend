from typing import Optional, Annotated

from pydantic import Field
from tortoise import Model, fields

from common import cfields
from common.backend.constaints import CitiesTypes
from common.orm.mixins import CRUDMixin
from src.users.entities import BaseUserRepo
from src.users.mixins import ManagerRepoFacetsMixin


class Manager(Model):
    """
    Менеджеры "Страны"
    """

    id: int = fields.BigIntField(description="ID", pk=True)
    name: str = fields.CharField(description='Имя', max_length=100)
    lastname: str = fields.CharField(description="Фамилия", max_length=100)
    patronymic: Optional[str] = fields.CharField(description='Отчество', null=True, max_length=100)
    position: Optional[str] = fields.CharField(description='Должность', null=True, max_length=512)
    phone: Optional[str] = fields.CharField(description='Телефон', null=True, max_length=20)
    work_schedule: Optional[str] = fields.CharField(description='Расписание работы', null=True, max_length=512)
    photo: Annotated[str, Field(max_length=2000)] = cfields.MediaField(
        description="Фотография", max_length=2000, null=True
    )
    city: str = cfields.CharChoiceField(
        description='Город менеджера', default=CitiesTypes.TYUMEN, choice_class=CitiesTypes, max_length=50, index=True,
    )
    email: Optional[str] = fields.CharField(
        description="Email", max_length=100, index=True, default='example@yandex.ru'
    )

    def __str__(self):
        return f'{self.lastname} {self.name} {self.patronymic}'

    class Meta:
        table = "users_managers"


class ManagersRepo(BaseUserRepo, ManagerRepoFacetsMixin, CRUDMixin):
    """
    Репозиторий менеджеров
    """
    model: Manager = Manager
