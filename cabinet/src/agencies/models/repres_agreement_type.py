from datetime import date

from ..entities import BaseAgencyModel


class ResponseAgreementType(BaseAgencyModel):
    """
    Модель типов документов
    """
    id: int
    name: str
    description: str
    priority: int
    created_at: date
    updated_at: date
