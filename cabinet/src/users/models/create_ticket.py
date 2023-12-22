from pydantic import validator, Field

from src.users.entities import BaseUserModel


class RequestCreateTicket(BaseUserModel):
    """
    Модель запроса создания заявки
    """
    name: str
    phone: str
    type: str
    city: str
    card_title: str | None = Field(description="Название карточки")

    @validator("phone")
    def normalize_phone(cls, phone_number: str) -> str:
        """
        Нормализация телефонного номера
        """
        # Remove all non-numeric characters
        normalized_number = ''.join(filter(str.isdigit, phone_number))

        if normalized_number.startswith('7'):
            normalized_number = '+7' + normalized_number[1:]

        return normalized_number

    class Config:
        orm_mode = True
