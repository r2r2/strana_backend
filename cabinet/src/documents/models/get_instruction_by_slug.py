from typing import Optional, Any
from pydantic import Field

from common.pydantic import CamelCaseBaseModel


class ResponseGetSlugInstructionModel(CamelCaseBaseModel):
    """
    Модель ответа получения инструкций.
    """

    slug: str
    link_text: str = Field(..., alias="label")
    file: Optional[dict[str, Any]]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
