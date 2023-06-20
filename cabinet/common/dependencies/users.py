from pytz import UTC
from http import HTTPStatus
from config import auth_config, redis_config
from datetime import datetime
from typing import Optional, Union, Any, Type
from fastapi import Depends, HTTPException, Header, WebSocket, Request, Body

from common.amocrm import AmoCRM
from src.users.exceptions import UserNotFoundError
from src.users.repos import UserRepo, User
from ..amocrm.exceptions import AmoNoContactError
from ..amocrm.types import AmoContact
from ..redis import Redis, broker as redis
from ..security import decode_access_token, oauth2_scheme
from ..session import SessionStorage


class CurrentAnyTypeUserId(object):
    """Получение id зарегистрированного пользователя, без указания роли"""

    def __call__(self, token: str = Depends(oauth2_scheme)) -> int:
        user_id, user_type, timestamp, _ = decode_access_token(token)
        if not user_id or not user_type or not timestamp:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if datetime.now(tz=UTC) > datetime.fromtimestamp(timestamp, tz=UTC):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id


class CurrentOptionalUserIdWithoutRole(object):
    """Необязательный ID текущего пользователя без указания роли"""

    def __call__(self, authorization: Optional[str] = Header(None)) -> Optional[int]:
        user_id: Optional[int] = None

        if authorization:
            scheme, token = authorization.split(" ")
            if scheme == auth_config["type"]:
                id, type, timestamp, _ = decode_access_token(token=token)
                if id and type and timestamp:
                    if datetime.now(tz=UTC) < datetime.fromtimestamp(
                            timestamp, tz=UTC
                    ):
                        user_id = id
        return user_id


class CurrentUserId(object):
    """
    ID текущего пользователя
    """

    def __init__(self, user_type: str) -> None:
        self.user_type: str = user_type

    def __call__(self, token: str = Depends(oauth2_scheme)) -> int:
        user_id, user_type, timestamp, _ = decode_access_token(token)
        if not user_id or not user_type or not timestamp:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if datetime.now(tz=UTC) > datetime.fromtimestamp(timestamp, tz=UTC):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if user_type != self.user_type:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id


class CurrentOptionalUserId(object):
    """
    Необязательный ID текущего пользователя
    """

    def __init__(self, user_type: str) -> None:
        self.user_type: str = user_type

    def __call__(self, authorization: Optional[str] = Header(None)) -> Union[int, None]:
        user_id = None
        if authorization:
            scheme, token = authorization.split(" ")
            if scheme == auth_config["type"]:
                id, type, timestamp, _ = decode_access_token(token=token)
                if id and type and timestamp:
                    if type == self.user_type and datetime.now(tz=UTC) < datetime.fromtimestamp(
                        timestamp, tz=UTC
                    ):
                        user_id: int = id
        return user_id



class DeletedUserCheck(object):
    """
    Проверка пользователя на удаление
    """

    def __init__(self, broker: Optional[Any] = None) -> None:
        self.redis: Redis = redis
        if broker:
            self.redis: Redis = broker

        self.redis_key: str = redis_config["deleted_users_key"]
        self.redis_expire: int = redis_config["deleted_users_expire"]

    async def __call__(self, request: Request) -> None:
        deleted: list[int] = await self.redis.lget(self.redis_key)
        deleted: list[int] = deleted if deleted else list()
        session: SessionStorage = request.session
        if session.auth is not None and isinstance(session.auth, dict):
            id: int = session.auth.get("id", None)
            if id is not None and str(id) in deleted:
                raise HTTPException(
                    status_code=HTTPStatus.FAILED_DEPENDENCY,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )


class CurrentUserExtra(object):
    """
    Экстра данные текущего пользователя
    """

    def __init__(self, key: Optional[str] = None) -> None:
        self.key: Union[str, None] = key

    def __call__(self, token: str = Depends(oauth2_scheme)) -> Any:
        decoded: tuple = decode_access_token(token)
        extra: dict[str, Any] = dict()
        if len(decoded) == 4:
            extra: dict[str, Any] = decoded[3]
        result: dict[str, Any] = dict()
        if self.key:
            result: Any = extra.get(self.key)
        return result


class WSCurrentUserId(object):
    """
    ID текущего пользователя для вебсокетов
    """

    def __init__(self, user_type: Optional[str] = None) -> None:
        self.user_type: Union[str, None] = user_type

    async def __call__(
        self, websocket: WebSocket, authorization: str = Header(None)
    ) -> Union[int, None]:
        # user_id = None
        # if not authorization:
        #     await websocket.close()
        # else:
        #     type, token = authorization.split(" ")
        #     user_id, user_type, timestamp = decode_access_token(token=token)
        #     if (
        #         not user_id
        #         or not type == auth_config["type"]
        #         or (self.user_type is not None and user_type != self.user_type)
        #         or datetime.now(tz=UTC) < datetime.fromtimestamp(timestamp, tz=UTC)
        #     ):
        #         await websocket.close()

        return 1230


class FetchedAmocrmContact:
    """Dependency for fetch amocrm contact"""

    async def __call__(self, amocrm_id: int = Body(..., embed=True)) -> AmoContact:
        async with await AmoCRM() as amocrm:
            contact: AmoContact = await amocrm.fetch_contact(user_id=amocrm_id)

        if not contact:
            raise AmoNoContactError
        return contact


class CurrentUserFromAmocrm:
    """Get current user from amocrm_id"""

    def __init__(self, users_repo: Type[UserRepo]):
        self.user_repo = users_repo()

    async def __call__(self, amo_contact: AmoContact = Depends(FetchedAmocrmContact())) -> int:
        user: User = await self.user_repo.retrieve(filters=dict(amocrm_id=amo_contact.id))
        if not user:
            raise UserNotFoundError
        return user.id
