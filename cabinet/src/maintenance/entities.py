from common.pydantic import CamelCaseBaseModel


class BaseMaintenanceModel(CamelCaseBaseModel):
    """
    Базовая модель обслуживания
    """
    class Config:
        orm_mode = True


class BaseMaintenanceCase:
    """
    Базовый сценарий обслуживания
    """


class BaseMaintenanceQuery:
    """
    Базовый запрос обслуживания
    """