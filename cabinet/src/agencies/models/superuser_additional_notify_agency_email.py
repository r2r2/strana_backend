from src.agencies.entities import BaseAgencyModel


class RequestAdditionalNotifyAgencyEmailModel(BaseAgencyModel):
    """
    Модель для получения данных для отправки писем представителям агентов при создании ДС в админке.
    """
    agency_id: int
    project_names: list[str]
