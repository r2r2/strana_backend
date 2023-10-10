from pydantic import BaseModel, constr, EmailStr, validator, Field

from common.utils import parse_phone


class DepregParticipantDTO(BaseModel):
    """
    Модель ответа DepregAPI [GET] /participants
    """
    id: int | None
    event_id: int | None = Field(alias="eventId")
    group_id: int | None = Field(alias="groupId")
    code: constr(max_length=255) | None
    name: str | None
    surname: str | None
    patronymic: str | None
    email: EmailStr | None
    phone: str | None
    company: str | None
    info: dict[str, str] | None
    marked: bool | None

    @validator("phone")
    def validate_phone(cls, value):
        """
        Валидация номера телефона
        """
        if value:
            phone = parse_phone(value)
            if not phone:
                raise ValueError(f"Некорректный номер телефона {value}")
            return phone
        return value

    class Config:
        orm_mode = True


class DepregParticipantsDTO(BaseModel):
    """
    Модель ответа DepregAPI [GET] /participants
    """
    data: list[DepregParticipantDTO]
