from common import cfields
from typing import Optional, Any
from tortoise import Model, fields

from common.orm.mixins import CreateMixin, RetrieveMixin
from ..entities import BasePageRepo


class ShowtimeRegistration(Model):
    """
    Запись на показ
    """

    id: int = fields.IntField(description="ID", pk=True)
    result_image: Optional[dict[str, Any]] = cfields.MediaField(
        description="Изображение результат", max_length=500, null=True
    )

    def __str__(self) -> str:
        return self.__doc__.strip()

    class Meta:
        table = "pages_showtime_registration"


class ShowtimeRegistrationRepo(BasePageRepo, CreateMixin, RetrieveMixin):
    """
    Репозиторий записи на показ
    """
    model = ShowtimeRegistration
