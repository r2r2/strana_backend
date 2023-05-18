from abc import ABC, abstractmethod
from typing import Any, Union

from ..requests import CommonResponse


class GetDocInterface(ABC):

    @property
    @abstractmethod
    def _auth_query(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def _request_get(self, url: str) -> CommonResponse:
        raise NotImplementedError

    @abstractmethod
    async def _request_post(self, payload: Union[dict[str, Any], list[Any]]) -> CommonResponse:
        raise NotImplementedError
