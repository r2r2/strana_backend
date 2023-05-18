from typing import Any

from ..entities import BaseAgentModel


class RequestAdminsAgentsSpecsModel(BaseAgentModel):
    """
    Модель запроса спеков агентов администратором
    """

    class Config:
        orm_mode = True


class ResponseAdminsAgentsSpecsModel(BaseAgentModel):
    """
    Модель ответа спеков агентов администратором
    """

    specs: dict[str, Any]
    ordering: list[Any]

    class Config:
        orm_mode = True
