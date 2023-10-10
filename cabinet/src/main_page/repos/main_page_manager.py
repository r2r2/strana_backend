from typing import Annotated, Optional

from common import cfields
from common.orm.entities import BaseRepo
from common.orm.mixins import ListMixin, RetrieveMixin
from pydantic import Field
from tortoise import Model, fields


class MainPageManager(Model):
    """
    Блок: Менеджер на главной
    """
    id: int = fields.IntField(description="ID", pk=True)
    name: str | None = fields.CharField(description='Имя', max_length=100, null=True)
    lastname: str | None = fields.CharField(
        description="Фамилия", max_length=100, null=True
    )
    patronymic: str | None = fields.CharField(
        description='Отчество', null=True, max_length=100,
    )
    position: str | None = fields.CharField(
        description='Должность', null=True, max_length=512
    )
    phone: str | None = fields.CharField(description='Телефон', null=True, max_length=20)
    work_schedule: str | None = fields.CharField(
        description='Расписание работы', null=True, max_length=512
    )
    photo: Annotated[str, Field(max_length=2000)] = cfields.MediaField(
        description="Фото", max_length=2000, null=True
    )
    email: str | None = fields.CharField(
        description="Email", max_length=100, null=True
    )

    def __str__(self):
        return f'{self.lastname} {self.name} {self.patronymic}'

    class Meta:
        table = "main_page_manager"


class MainPageManagerRepo(BaseRepo, RetrieveMixin, ListMixin):
    """
    Репозиторий менеджера главной страницы
    """
    model = MainPageManager
