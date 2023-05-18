from typing import Any, Optional
from config import session_config

from ..wrappers import mark_async
from ..redis import broker as redis, Redis


@mark_async
class SessionStorage(object):
    """
    Storage of session data
    """

    async def __ainit__(self, session_id: str, broker: Optional[Any] = None) -> None:
        self.redis: Redis = redis
        if broker:
            self.redis: Redis = broker

        self.session_id: str = session_id

        self.expire: int = session_config["expire"]
        self.auth_attempts_expire: int = session_config["auth_attempts_expire"]

        self.auth_key: str = session_config["auth_key"]
        self.auth_attempts_key: str = session_config["auth_attempts_key"]
        self.document_key: str = session_config["document_key"]
        self.password_reset_key: str = session_config["password_reset_key"]
        self.password_settable_key: str = session_config["password_settable_key"]

        self.data: dict[str, Any] = await self.redis.get(key=self.session_id)

        if self.data is None:
            self.data: dict[str, Any] = dict()
            await self.redis.set(key=self.session_id, value=self.data, expire=self.expire)

    async def set(self, key: str, value: Any, expire: int = None) -> bool:
        """
        Set value to session storage by key
        """
        self.data[key]: Any = value
        expire: int = expire or self.expire
        ok: bool = await self.redis.set(key=self.session_id, value=self.data, expire=expire)
        if not ok:
            self.data.pop(key)
        return ok

    async def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get value from session storage by key
        """
        data: dict[str, Any] = await self.redis.get(key=self.session_id)
        data: Any = data.get(key)
        if data is None:
            data: Any = default
        return data

    async def insert(self) -> None:
        """
        Insert current self.data state to redis
        """
        await self.redis.set(key=self.session_id, value=self.data, expire=self.expire)

    async def prune(self) -> None:
        """
        Clear redis data
        """
        await self.redis.set(key=self.session_id, value=dict(), expire=self.expire)

    async def pop(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Pop value from self.data and insert updated state to redis
        """
        value: Any = self.data.pop(key, default)
        await self.insert()
        return value

    async def refresh(self) -> None:
        """
        Refresh current session state
        """
        self.data: dict[str, Any] = await self.redis.get(key=self.session_id)

    @property
    def auth(self) -> Any:
        return self.data.get(self.auth_key)

    @property
    def document(self) -> Any:
        return self.data.get(self.document_key)

    @property
    def password_rest(self) -> Any:
        return self.data.get(self.password_reset_key)

    @property
    def password_settable(self) -> Any:
        return self.data.get(self.password_settable_key)

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.data[key]: Any = value

    def __delitem__(self, key: str) -> None:
        del self.data[key]

    def __str__(self) -> str:
        return str(self.data)
