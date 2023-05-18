# pylint: disable=useless-parent-delegation

from typing import Any, Optional

from pydantic import BaseModel


class AmoCustomFieldValue(BaseModel):
    value: Optional[Any] = None
    enum_id: Optional[int] = None
    enum_code: Optional[str] = None


class AmoCustomField(BaseModel):
    field_id: int
    field_name: Optional[str]
    field_code: Optional[str] = None
    field_type: Optional[str] = None
    values: list[AmoCustomFieldValue]


class AmoModel(BaseModel):
    custom_fields_values: Optional[list[AmoCustomField]] = []

    def dict(self, *, by_alias: bool = True, **kwargs) -> dict:
        return super().dict(by_alias=by_alias, **kwargs)


class AmoTag(BaseModel):
    id: Optional[int] = None
    name: Optional[str]
    color: Optional[str] = None


class EmbeddedDTO(BaseModel):
    tags: Optional[list[AmoTag]] = []
