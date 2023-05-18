from typing import Optional

from common.files.models import FileCategoryListModel
from pydantic import NoneStr

from ..entities import BaseAgencyModel


class _AgentListModel(BaseAgencyModel):
    """
    Модель агента в списке
    """

    id: int
    name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]

    class Config:
        orm_mode = True


class _MaintainerRetrieveModel(BaseAgencyModel):
    """
    Модель детального администратора
    """

    name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]

    class Config:
        orm_mode = True


class ResponseAdminsAgenciesRetrieveModel(BaseAgencyModel):
    """
    Модель ответа детального агенства администратором
    """

    id: int
    is_approved: bool
    name: Optional[str]
    inn: NoneStr
    city: NoneStr
    active_clients: Optional[int]
    closed_clients: Optional[int]
    succeed_clients: Optional[int]
    agents: Optional[list[_AgentListModel]]
    files: Optional[list[FileCategoryListModel]]
    maintainer: Optional[_MaintainerRetrieveModel]

    class Config:
        orm_mode = True
