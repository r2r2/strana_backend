from typing import Optional

from pydantic import BaseModel


class AgentBaseModel(BaseModel):
    """
    Модель агента пользователя
    """

    id: int
    phone: Optional[str]
    email: Optional[str]
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]

    class Config:
        orm_mode = True


class AgentRetrieveModel(AgentBaseModel):
    pass
