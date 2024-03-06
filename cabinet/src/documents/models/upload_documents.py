from uuid import UUID

from pydantic import Field

from src.documents.entities import BaseDocumentModel


class ResponseUploadDocumentsSchema(BaseDocumentModel):
    """
    Схема для загрузки документов
    """
    id: UUID = Field(description="UID")
    file_name: str = Field(description="Название файла", alias='name')
    url: str = Field(description="URL загруженного файла")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class ResponseDeleteDocumentsSchema(BaseDocumentModel):
    """
    Схема ответа для удаления документов
    """
    id: UUID = Field(..., description="UID")
    file_name: str = Field(..., description="Название файла", alias='name')

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class RequestDeleteDocumentsSchema(BaseDocumentModel):
    """
    Схема для запроса на удаление документов
    """
    file_ids: list[UUID] = Field(..., description="ID документов для удаления")
    document_id: int = Field(..., description="ID типа поля документа")
    booking_id: int = Field(..., description="ID бронирования")

    class Config:
        orm_mode = True


class UploadedDocumentSchema(BaseDocumentModel):
    """
    Схема для загруженного документа
    """
    id: UUID = Field(..., description="UUID")
    file_name: str = Field(..., description="Название файла", alias='name')

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
