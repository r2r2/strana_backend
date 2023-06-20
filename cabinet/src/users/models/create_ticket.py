from src.users.entities import BaseUserModel


class RequestCreateTicket(BaseUserModel):
    """
    Модель запроса создания заявки
    """
    name: str
    phone: str
    type: str
    city: str

    class Config:
        orm_mode = True
