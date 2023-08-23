from typing import Optional, Any

from pydantic import Field, root_validator

from src.users.entities import BaseCheckModel


class RequestAgentsUsersCheckDisputeModel(BaseCheckModel):
    user_id: int = Field(alias="userId")
    comment: Optional[str]

    class Config:
        orm_mode = True


class ResponseAgentUsersCheckDisputeModel(BaseCheckModel):
    user_id: int
    unique_status: Optional[Any]
    status: Optional[Any]

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
