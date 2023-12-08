from fastapi import status

from .entities import BaseNewsException


class NewsNotFoundError(BaseNewsException):
    message: str = "Новость не найдена"
    status: int = status.HTTP_404_NOT_FOUND
    reason: str = "news_not_found"


class UserHasNotSeenNewsError(BaseNewsException):
    message: str = "Пользователь еще не просматривал новость"
    status: int = status.HTTP_400_BAD_REQUEST
    reason: str = "user_has_not_seen_news"


class UserAlreadyVoteNewsError(BaseNewsException):
    message: str = "Пользователь уже проголосовал за новость"
    status: int = status.HTTP_400_BAD_REQUEST
    reason: str = "user_already_vote_news"
