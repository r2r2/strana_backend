from typing import Optional

from ..constants import UserStatus
from ..entities import BaseCheckModel


class RequestAgentsUsersCheckDisputeModel(BaseCheckModel):
    user_id: int
    comment: Optional[str]

    class Config:
        orm_mode = True


class ResponseAgentUsersCheckDisputeModel(BaseCheckModel):
    user_id: int
    status: UserStatus.serializer

    class Config:
        orm_mode = True
