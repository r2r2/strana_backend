from typing import Any

from ..entities import BaseAgentModel


class RequestRepresesAgentsSpecsModel(BaseAgentModel):
    """
    Модель запроса спеков агентов представителя агенства
    """

    class Config:
        orm_mode = True


class ResponseRepresesAgentsSpecsModel(BaseAgentModel):
    """
    Модель ответа спеков агентов представителя агенства
    """

    specs: dict[str, Any]
    ordering: list[Any]

    class Config:
        orm_mode = True
