from typing import Any, Optional

from ..entities import BaseAgentModel


class RequestRepresesAgentsListModel(BaseAgentModel):
    """
    Модель запроса списка агентов представителя агенства
    """

    class Config:
        orm_mode = True


class _AgentListModel(BaseAgentModel):
    """
    Модель агента в списке
    """

    id: int
    is_approved: bool
    name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]
    active_clients: Optional[int]
    succeed_clients: Optional[int]

    class Config:
        orm_mode = True


class ResponseRepresesAgentsListModel(BaseAgentModel):
    """
    Модель ответа списка агентов представителя агенства
    """

    count: int
    page_info: dict[str, Any]
    result: list[_AgentListModel]

    class Config:
        orm_mode = True
