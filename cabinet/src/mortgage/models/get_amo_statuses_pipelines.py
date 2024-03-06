from pydantic import Field

from src.mortgage.entities import BaseMortgageSchema


class _PipelinesSchema(BaseMortgageSchema):
    """
    Схема воронок Амо
    """
    id: int = Field(..., description="ID воронки")
    name: str = Field(..., description="Название воронки")


class _StatusesSchema(BaseMortgageSchema):
    """
    Схема статусов Амо
    """
    id: int = Field(..., description="ID статуса")
    name: str = Field(..., description="Название статуса")
    pipeline_id: int = Field(..., description="ID воронки")


class AmoStatusesPipelinesSchema(BaseMortgageSchema):
    """
    Схема статусов и воронок Амо
    """
    statuses: list[_StatusesSchema] = Field(..., description="Статусы")
    pipelines: list[_PipelinesSchema] = Field(..., description="Воронки")
