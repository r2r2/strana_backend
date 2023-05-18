from typing import Optional

from ..entities import BaseUserModel
from ..constants import UserStatus


class RequestAdminCommentModel(BaseUserModel):
    user_id: int
    comment: Optional[str]


class ResponseAdminCommentModel(BaseUserModel):
    status: UserStatus.serializer
    admin_comment: Optional[str]

    class Config:
        orm_mode = True
