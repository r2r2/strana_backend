from datetime import datetime
from typing import Any, Optional

from pydantic import root_validator, Field, parse_obj_as

from ..entities import BaseNewsModel


class NewsTagModel(BaseNewsModel):
    """
    Модель тегов новостей.
    """

    id: int
    label: str
    slug: str

    class Config:
        orm_mode = True


class NewsCityModel(BaseNewsModel):
    """
    Модель городов новостей.
    """

    id: int
    name: str
    slug: str

    class Config:
        orm_mode = True


class NewsProjectModel(BaseNewsModel):
    """
    Модель проектов новостей.
    """

    id: int
    name: str
    slug: str
    city: Optional[NewsCityModel]

    class Config:
        orm_mode = True


class NewsModel(BaseNewsModel):
    """
    Общая модель новостей.
    """

    id: int
    title: Optional[str]
    slug: str
    pub_date: Optional[datetime]
    end_date: Optional[datetime]

    # Method fields
    news_projects: Any
    active_tags: Any

    @root_validator
    def get_projects_and_tags_info(cls, values: dict[str, Any]) -> dict[str, Any]:
        """
        Получение информации по проектам и тегам новостей.
        """

        projects: Any = values.pop("news_projects", None)
        tags: Any = values.pop("active_tags", None)

        # сортируем теги по приоритету
        tags.sort(key=lambda x: x.priority)

        values["projects"] = [parse_obj_as(NewsProjectModel, project) for project in projects]
        values["tags"] = [parse_obj_as(NewsTagModel, tag) for tag in tags]

        return values

    class Config:
        orm_mode = True


class ResponseNewsInListModel(NewsModel):
    """
    Модель для списка новостей.
    """

    short_description: Optional[str]
    image_preview: Optional[dict[str, Any]]
    is_shown: bool

    class Config:
        orm_mode = True


class ResponseDetailNewsModel(NewsModel):
    """
    Модель для деталки новостей.
    """

    description: Optional[str]
    image: Optional[dict[str, Any]]

    # Method fields
    is_voice_left: bool
    is_useful: Optional[bool]

    @root_validator
    def get_voted_info(cls, values: dict[str, Any]) -> dict[str, Any]:
        """
        Получение информации по полезности новости для пользователя.
        """

        is_voice_left: bool = values.pop("is_voice_left", None)
        is_useful: Optional[bool] = values.pop("is_useful", None)

        values["is_useful"] = is_useful if is_voice_left else None

        return values

    class Config:
        orm_mode = True


class ResponseNewsListModel(BaseNewsModel):
    """
    Модель ответа списка новостей.
    """

    count: int
    page_info: dict[str, Any]
    result: list[ResponseNewsInListModel]

    class Config:
        orm_mode = True


class RequestUserVoteNewsModel(BaseNewsModel):
    """
    Модель запроса для апи голосования о полезности новости для пользователя.
    """

    is_useful: bool

