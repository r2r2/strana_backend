from src.agencies.entities import BaseAgencyModel


class RequestAgencyAdditionalAgreementModel(BaseAgencyModel):
    """
    Модель данных для создания дополнительных соглашений
    """
    agency_id: int
    project_ids: list[int]


class RequestAgencyAdditionalAgreementListModel(BaseAgencyModel):
    """
    Модель создания дополнительных соглашений
    """
    comment: str
    agencies: list[RequestAgencyAdditionalAgreementModel]
