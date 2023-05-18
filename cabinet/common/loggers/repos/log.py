from datetime import datetime
from typing import Optional, Union

from tortoise import fields


class AbstractLogMixin:
    """
    Абстрактный миксин логов
    """

    id: int = fields.BigIntField(description="ID", pk=True)
    created: datetime = fields.DatetimeField(description="Создано", auto_now=True)
    state_before: Optional[Union[list, dict]] = fields.JSONField(
        description="Состояние до", null=True
    )
    state_after: Optional[Union[list, dict]] = fields.JSONField(
        description="Состояние после", null=True
    )
    state_difference: Optional[Union[list, dict]] = fields.JSONField(
        description="Разница состояний", null=True
    )
    content: Optional[str] = fields.TextField(description="Контент", null=True)
    error_data: Optional[str] = fields.TextField(description="Данные ошибки", null=True)
    response_data: Optional[str] = fields.TextField(description="Данные ответа", null=True)
    use_case: Optional[str] = fields.CharField(description="Сценарий", max_length=200, null=True)
