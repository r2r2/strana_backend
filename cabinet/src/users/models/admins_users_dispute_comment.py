from typing import Optional, Any

from pydantic import root_validator

from src.users.entities import BaseUserModel


class RequestAdminCommentModel(BaseUserModel):
    user_id: int
    comment: Optional[str]


class ResponseAdminCommentModel(BaseUserModel):
    status: Any
    unique_status: Optional[Any]
    admin_comment: Optional[str]

    @root_validator
    def set_status(cls, values):
        if unique_status := values.pop("unique_status"):
            values["status"] = {
                "value": unique_status.slug,
                "label": f"{unique_status.title} {unique_status.subtitle or ''}".strip(),
            }
        return values

    class Config:
        orm_mode = True

        # @staticmethod
        # def schema_extra(schema: dict[str, Any]) -> None:
        #     schema["properties"].pop("unique_status")
