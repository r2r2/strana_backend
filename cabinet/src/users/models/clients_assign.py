from typing import Optional
from pydantic import BaseModel, Field, validator, constr, EmailStr

from common.utils import parse_phone
from ..exceptions import UserIncorrectPhoneFormatError


class RequestAssignClient(BaseModel):
    name: str
    surname: Optional[str] = ''
    patronymic: Optional[str] = ''
    email: Optional[EmailStr]
    phone: constr(min_length=9)
    check_id: int = Field(..., description='id проверки')
    user_id: Optional[int]
    active_projects: Optional[list[int]] = Field(default=[], description='Активные ЖК(проекты)')
    agency_contact: Optional[str] = ''
    assignation_comment: Optional[str] = ''
    consultation_type: str

    @validator('phone')
    def validate_phone(cls, phone: str) -> str:
        phone: Optional[str] = parse_phone(phone)
        if not phone:
            raise UserIncorrectPhoneFormatError
        return phone

    @property
    def full_name(self):
        return f'{self.surname} {self.name} {self.patronymic}'.strip()

    @property
    def user_data(self):
        """Данные для update модели юзера"""
        return self.dict(exclude={'check_id', 'user_id', 'active_projects'})


class ResponseAssignClient(BaseModel):
    agent_id: int
    agency_id: int
    client_id: int = Field(alias='id')
    bookingId: Optional[int] = Field(default=None, alias='booking_id')

    class Config:
        orm_mode = True
