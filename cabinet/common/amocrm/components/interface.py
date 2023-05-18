from abc import ABC, abstractmethod
from typing import Any, Union

from ...requests import CommonResponse


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
