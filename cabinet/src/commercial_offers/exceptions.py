from fastapi import status
from .entities import BaseOfferException


class LeadNotFoundError(BaseOfferException):
    message: str = "Сделка не найдена."
    status: int = status.HTTP_404_NOT_FOUND
    reason: str = "lead_not_found"


class ClientNotFoundError(BaseOfferException):
    message: str = "Клиент не найден."
    status: int = status.HTTP_404_NOT_FOUND
    reason: str = "client_not_found"
