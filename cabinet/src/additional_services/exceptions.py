from fastapi import status

from .entities import BaseAdditionalServiceException


class AdditionalServiceNotFoundError(BaseAdditionalServiceException):
    message: str = "Доп. услуга не найдена."
    status: int = status.HTTP_404_NOT_FOUND
    reason: str = "additional_service_not_found"
