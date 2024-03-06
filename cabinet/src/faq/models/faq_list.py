from typing import Optional

from pydantic import Field

from ..entities import BaseFAQModel


class _FAQModel(BaseFAQModel):
    """
    Модель FAQ
    """

    id: int
    slug: str
    is_active: bool
    order: int
    question: str
    answer: str
    page_type_id: str | None = Field(alias="pageTypeSlug")

    class Config:
        orm_mode = True


class ResponseFAQListModel(BaseFAQModel):
    """
    Модель ответа списка FAQ
    """

    count: int
    result: Optional[list[_FAQModel]]

    class Config:
        orm_mode = True
