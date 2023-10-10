import re

from pydantic import validator, constr

from common.utils import parse_phone
from src.users.exceptions import UserIncorrectPhoneFormatError
from ..entities import BaseAdditionalServiceCamelCaseModel


class CreateTicketRequest(BaseAdditionalServiceCamelCaseModel):
    """
    Модель запроса для создания заявки
    """

    full_name: constr(min_length=1, max_length=50)
    phone: str
    service_id: int
    booking_id: int | None

    @validator("phone")
    def validate_phone(cls, phone: str) -> str:
        """
        Валидация номера телефона
        """
        phone: str = parse_phone(phone)
        if re.compile(r"^(8|\+7)\d{10}$").match(phone):
            return phone
        raise UserIncorrectPhoneFormatError


class CreatedTicketResponse(BaseAdditionalServiceCamelCaseModel):
    """
    Модель ответа созданной заявки
    """

    full_name: str
    phone: str
    service_id: int
    booking_id: int | None
    status_id: int | None


class _TicketGroupStatusResponse(BaseAdditionalServiceCamelCaseModel):
    name: str
    sort: int


class _TicketCategoryResponse(BaseAdditionalServiceCamelCaseModel):
    title: str


class _TicketServiceResponse(BaseAdditionalServiceCamelCaseModel):
    title: str
    category: _TicketCategoryResponse

    class Config:
        orm_mode = True


class _TicketResponse(BaseAdditionalServiceCamelCaseModel):
    """
    Модель ответа созданной заявки
    """

    id: int
    booking_id: int | None
    group_status: _TicketGroupStatusResponse
    service: _TicketServiceResponse

    class Config:
        orm_mode = True


class _TemplateResponse(BaseAdditionalServiceCamelCaseModel):
    """
    Модель ответа шаблона для заявки
    """

    title: str
    description: str
    button_text: str


class TicketListResponse(BaseAdditionalServiceCamelCaseModel):
    """
    Модель ответа списка агенств администратором
    """

    count: int
    page_info: dict
    result: list[_TicketResponse]
    template: _TemplateResponse | None
    statuses: list[_TicketGroupStatusResponse]
