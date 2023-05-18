from src.represes.entities import BaseRepresModel


class RequestInitializeChangePhone(BaseRepresModel):
    phone: str


class RequestInitializeChangeEmail(BaseRepresModel):
    email: str
