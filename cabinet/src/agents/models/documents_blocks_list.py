from typing import Optional
from uuid import UUID

from pydantic import root_validator, Field

from common.pydantic import CamelCaseBaseModel


class UploadFile(CamelCaseBaseModel):
    id: UUID
    file_name: Optional[str] = Field(alias="name")


class _DocumentResponse(CamelCaseBaseModel):
    id: int
    label: Optional[str]
    required: bool
    attachments: list[Optional[UploadFile]]

    class Config:
        orm_mode = True


class DocumentBlockResponse(CamelCaseBaseModel):
    title: Optional[str]
    description: Optional[str] # запихиваем в hint
    label: Optional[str] # запихиваем в hint
    hint: Optional[dict]
    fields: list[_DocumentResponse]

    @root_validator
    def _get_hint(cls, values: dict):
        hint: dict = dict()
        hint["label"] = values.get("label")
        hint["description"] = values.get("description")
        if "label" in values:
            del values["label"]
        if "description" in values:
            del values["description"]
        values["hint"] = hint
        return values

    class Config:
        orm_mode = True
