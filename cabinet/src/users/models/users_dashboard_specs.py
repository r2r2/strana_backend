from ..entities import BaseUserModel, BaseUserCamelCaseModel


class CityModel(BaseUserModel):
    """
    Модель города
    """
    name: str
    slug: str


class ResponseDashboardSpec(BaseUserCamelCaseModel):
    """
    Модель ответа на запрос спецификации
    """
    active_bookings: int
    completed_bookings: int
    interests: int
    notifications: int
    min_property_price: int
