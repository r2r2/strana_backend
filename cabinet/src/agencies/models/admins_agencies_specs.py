from typing import Any

from ..entities import BaseAgencyModel


class RequestAdminsAgenciesSpecsModel(BaseAgencyModel):
    """
    Модель запроса спеков агенств администратором
    """

    class Config:
        orm_mode = True


class ResponseAdminsAgenciesSpecsModel(BaseAgencyModel):
    """
    Модель ответа спеков агенств администратором
    """

    specs: dict[str, Any]
    ordering: list[Any]

    class Config:
        orm_mode = True
