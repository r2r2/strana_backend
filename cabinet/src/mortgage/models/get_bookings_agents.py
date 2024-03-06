from typing import Any

from pydantic import Field, root_validator

from src.mortgage.entities import BaseMortgageSchema


class BookingsAgentsSchema(BaseMortgageSchema):
    id: int = Field(..., description="ID брони")
    amocrm_id: int = Field(..., description="ID брони в AMO")
    active: bool = Field(..., description="Активность брони")
    amocrm_status_id: int | None = Field(description="ID статуса брони в AMO")
    agent_id: int | None = Field(description="ID агента")
    name: str | None = Field(description="Имя агента", alias="agent__name")
    surname: str | None = Field(description="Фамилия агента", alias="agent__surname")
    patronymic: str | None = Field(description="Отчество агента", alias="agent__patronymic")
    phone: str | None = Field(description="Телефон агента", alias="agent__phone")
    email: str | None = Field(description="Email агента", alias="agent__email")
    agent_amocrm_id: int | None = Field(description="ID агента в AMO", alias="agent__amocrm_id")
    building_name: str | None = Field(description="Название ЖК", alias="building__name")
    property_rooms: int | None = Field(description="Количество комнат", alias="property__rooms")
    property_number: str | None = Field(description="Номер квартиры", alias="property__number")
    property_area: float | None = Field(description="Площадь", alias="property__area")
    property_price: float | None = Field(description="Цена", alias="property__price")
    floor_number: str | None = Field(description="Этаж", alias="floor__number")
    project_name: str | None = Field(description="Название проекта", alias="project__name")
    user_id: int | None = Field(description="ID пользователя")
    property_active: bool | None = Field(description="Активность квартиры", alias="property__property_type__is_active")
    property_plan: Any = Field(description="URL Планировки", alias="property__plan")

    @root_validator
    def validate_values(cls, values: dict[str, Any]) -> dict[str, Any]:
        if plan := values.get("property_plan"):
            values["property_plan"] = plan["aws"]  # plan["s3"] | plan["src"]
        return values
