from datetime import datetime
from typing import Optional, Any

from common.utils import parse_phone
from pydantic import EmailStr, constr, validator, root_validator, Field, parse_obj_as

from src.users.entities import BaseUserModel, BaseCheckModel
from src.users.exceptions import UserIncorrectPhoneForamtError
from src.users.repos.unique_status import IconType


class RequestUsersCheckModel(BaseUserModel):
    """
    Модель запроса проверки пользователя агентом на уникальность
    """

    phone: constr(min_length=9)
    email: Optional[EmailStr]
    name: Optional[constr(max_length=50)]
    surname: Optional[constr(max_length=50)]
    patronymic: Optional[constr(max_length=50)]

    @validator('phone')
    def validate_phone(cls, phone: str) -> str:
        """
        Валидация номера телефона
        """
        phone: Optional[str] = parse_phone(phone)
        if not phone:
            raise UserIncorrectPhoneForamtError
        return phone

    class Config:
        orm_mode = True


class ButtonSchema(BaseCheckModel):
    text: Optional[str]
    background_color: Optional[str]
    text_color: Optional[str]
    description: Optional[str]

    class Config:
        orm_mode = True


class UniqueStatusSchema(BaseCheckModel):
    slug: Optional[str] = Field(alias="value")
    title: Optional[str]
    subtitle: Optional[str]
    icon: Optional[IconType.serializer]
    color: Optional[str]
    background_color: Optional[str]
    border_color: Optional[str]

    class Config:
        orm_mode = True


class ResponseUsersCheckModel(BaseCheckModel):
    """
    Модель ответа проверки пользователя агентом на уникальность
    """

    id: Optional[int]
    user_id: Optional[int]
    agent_id: Optional[int]
    agency_id: Optional[int]
    requested: Optional[datetime]
    unique_status: Optional[Any]
    status: Optional[UniqueStatusSchema]
    can_dispute: Optional[bool]
    button: Optional[ButtonSchema]

    @root_validator
    def get_unique_status(cls, values: dict[str, Any]) -> dict[str, Any]:
        """unique status"""
        if unique_status := values.pop("unique_status"):
            values["status"] = parse_obj_as(UniqueStatusSchema, unique_status)
            values["can_dispute"] = unique_status.can_dispute
        return values

    class Config:
        orm_mode = True
