from enum import Enum
from datetime import datetime, date
from typing import Optional, Any

from pydantic import BaseModel, validator

from src.agencies.constants import AgencyType
from ..constants import UserStatusCheck
from ..entities import BaseUserModel


class HistoryCheckStatusType(str, Enum):
    UNIQUE: str = "unique"
    NOT_UNIQUE: str = "not_unique"
    CAN_DISPUTE: str = "can_dispute"


class HistoryCheckDate(str, Enum):
    DATE_UP: str = "created_at"
    DATE_DOWN: str = "-created_at"
    STATUS_TYPE: str = "status"


class HistoryCheckSearchFilters(BaseModel):
    search: Optional[str]
    ordering: Optional[HistoryCheckDate]
    start_date: Optional[date]
    end_date: Optional[date]

    @validator("search")
    def replace_to_plus(cls, phone_number: str):
        new_number: str = phone_number.replace(" 7", "+7") if phone_number else None
        return new_number


class _UserHistoryCheckRetrieveModel(BaseUserModel):
    """
    Модель пользователя
    """

    id: int
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]
    amocrm_id: Optional[int]
    phone: Optional[str]
    email: Optional[str]

    class Config:
        orm_mode = True


class _AgencyHistoryCheckRetrieveModel(BaseModel):
    id: int
    amocrm_id: Optional[str]
    name: Optional[str]
    type: Optional[AgencyType.serializer]

    class Config:
        orm_mode = True


class AdminHistoryCheckModel(BaseModel):
    """
    Модель истории проверки пользователя
    """
    id: int
    client: Optional[_UserHistoryCheckRetrieveModel]
    client_phone: Optional[str]
    status_pin: Optional[dict] # функционал будет реализован в будущем
    agent: Optional[_UserHistoryCheckRetrieveModel]
    agency: Optional[_AgencyHistoryCheckRetrieveModel]
    status: Optional[UserStatusCheck.serializer]
    created_at: datetime

    class Config:
        orm_mode = True


class AdminHistoryCheckAggregatorModel(BaseModel):
    unique_count: int = 0
    not_unique_count: int = 0
    can_dispute_count: int = 0


class ResponseAdminHistoryCheckListModel(BaseUserModel):
    """
    Модель ответа списка истории пользователей администратором
    """
    count: int
    page_info: dict[str, Any]
    aggregators: AdminHistoryCheckAggregatorModel
    result: list[AdminHistoryCheckModel]

    class Config:
        orm_mode = True
