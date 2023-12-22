from pydantic import Field

from src.mortgage.entities import BaseMortgageCamelCaseSchema


class MortgageTextBlockResponseSchema(BaseMortgageCamelCaseSchema):
    """
    Схема ответа на запрос текстового блока
    """
    id: int
    title: str | None = Field(description="Заголовок")
    text: str | None = Field(description="Текст")
    description: str | None = Field(description="Описание")
    slug: str = Field(..., description="Слаг")
    lk_type: str | None = Field(description="Тип ЛК")
