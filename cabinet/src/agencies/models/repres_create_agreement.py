from src.agencies.entities import BaseAgencyModel


class RequestAgencyAgreementModel(BaseAgencyModel):
    """
    Модель создания договора
    """
    projects: list[int]
    type_id: int
