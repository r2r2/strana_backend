from typing import Optional

from pydantic import BaseModel


class FileListModel(BaseModel):
    """
    Модель файла в списке
    """

    aws: Optional[str]
    hash: Optional[str]
    name: Optional[str]
    source: Optional[str]
    mb_size: Optional[int]
    kb_size: Optional[int]
    extension: Optional[str]
    content_type: Optional[str]

    class Config:
        orm_mode = True


class FileCategoryListModel(BaseModel):
    """
    Модель категории файла в списке
    """

    name: Optional[str]
    slug: Optional[str]
    count: Optional[int]
    files: Optional[list[FileListModel]]

    class Config:
        orm_mode = True
