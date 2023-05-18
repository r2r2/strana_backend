from pydantic import BaseModel


class StatusTypeUnique(BaseModel):
    value: str = "unique"
    label: str = "Уникальный"


class StatusTypeNotUnique(BaseModel):
    value: str = "not_unique"
    label: str = "Неуникальный"


class StatusTypeCanDispute(BaseModel):
    value: str = "can_dispute"
    label: str = "Закреплен, но можно оспорить"


class OrderingStatus(BaseModel):
    value: str = "status"
    label: str = "По статусу уникальности"


class OrderingDateUp(BaseModel):
    value: str = "created_at"
    label: str = "По дате (от старых к новым)"


class OrderingDateDown(BaseModel):
    value: str = "-created_at"
    label: str = "По дате (от новых к старым)"


class AdminHistorySpecs(BaseModel):
    status_type: list = [StatusTypeUnique(), StatusTypeNotUnique(), StatusTypeCanDispute()]


class AdminHistoryCheckSpecs(BaseModel):
    specs: dict = AdminHistorySpecs()
    ordering: list = [OrderingStatus(), OrderingDateUp(), OrderingDateDown()]
