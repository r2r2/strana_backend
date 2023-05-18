from typing import Optional, Any
from pydantic import root_validator as method_field

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
