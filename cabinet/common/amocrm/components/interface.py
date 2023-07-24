from abc import ABC, abstractmethod, ABCMeta
from functools import wraps
from typing import Any, Union, Optional

# from aiolimiter import AsyncLimiter

from config import request_limiter_config
from ...requests import CommonResponse


# class RateLimitSingleton:
#     _max_requests: float = request_limiter_config["max_requests"]
#     _period: float = request_limiter_config["period"]
#     _rate_limiter: Optional[AsyncLimiter] = None
#
#     @classmethod
#     def get_rate_limiter(cls) -> AsyncLimiter:
#         if not cls._rate_limiter:
#             cls._rate_limiter = AsyncLimiter(cls._max_requests, cls._period)
#         return cls._rate_limiter
#
#
# def rate_limit_decorator(func):
#     rate_limiter = RateLimitSingleton.get_rate_limiter()
#
#     @wraps(func)
#     async def wrapper(self, *args, **kwargs):
#         async with rate_limiter:
#             return await func(self, *args, **kwargs)
#
#     return wrapper
#
#
# class RateLimitMeta(ABCMeta):
#     def __new__(cls, name, bases, attrs):
#         decorated_attrs = {}
#
#         rate_limit = attrs.get("rate_limit_decorator")
#         if rate_limit is None:
#             rate_limit = rate_limit_decorator
#
#         for attr_name, attr_value in attrs.items():
#
#             if callable(attr_value) and '_request' in attr_name:
#                 decorated_attrs[attr_name] = rate_limit(attr_value)
#             else:
#                 decorated_attrs[attr_name] = attr_value
#
#         decorated_attrs["rate_limit"] = rate_limit
#
#         return super().__new__(cls, name, bases, decorated_attrs)


class AmoCRMInterface(ABC):
    """
    Base amocrm interface
    """

    @property
    @abstractmethod
    def _auth_headers(self) -> dict[str, str]:
        raise NotImplementedError

    @abstractmethod
    async def _fetch_settings(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def _refresh_auth(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def _update_settings(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def _request_get(self, route: str, query: dict[str, Any]) -> CommonResponse:
        raise NotImplementedError

    @abstractmethod
    async def _request_get_v4(self, route: str, query: dict[str, Any]) -> CommonResponse:
        raise NotImplementedError

    @abstractmethod
    async def _request_post(self, route: str,
                            payload: Union[dict[str, Any], list[Any]]) -> CommonResponse:
        raise NotImplementedError

    @abstractmethod
    async def _request_post_v4(
            self, route: str, payload: Union[dict[str, Any], list[Any]]) -> CommonResponse:
        raise NotImplementedError

    @abstractmethod
    async def _request_patch(
            self, route: str, payload: Union[dict[str, Any], list[Any]]) -> CommonResponse:
        raise NotImplementedError

    @abstractmethod
    async def _request_patch_v4(self, route: str,
                                payload: Union[dict[str, Any], list[Any]]) -> CommonResponse:
        raise NotImplementedError
