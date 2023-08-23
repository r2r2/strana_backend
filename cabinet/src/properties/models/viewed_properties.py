from datetime import datetime

from common.pydantic import CamelCaseBaseModel


class ViewedPropertyResponse(CamelCaseBaseModel):
    """
    Модель ответа добавленного объекта недвижимости
    """
    id: int
    client_id: int
    property_id: int
    updated_at: datetime
    created_at: datetime
