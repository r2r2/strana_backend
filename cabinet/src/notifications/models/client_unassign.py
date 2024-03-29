from typing import Optional

from pydantic import BaseModel, Field


class ResponseUnassignText(BaseModel):
    title: str = Field(..., description='Заголовок страницы открепления клиента')
    text: str = Field(..., description='Текст для страницы открепления клиента')

    class Config:
        orm_mode = True


class ResponseSMSText(BaseModel):
    text: Optional[str] = Field(description='Текст для отправки смс')

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
