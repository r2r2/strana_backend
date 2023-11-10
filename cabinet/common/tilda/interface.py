from typing import Union, Any
from abc import ABC, abstractmethod, ABCMeta

from common.requests.responses import CommonResponse


class TildaInterface(ABC):
    """
    Base amocrm interface
    """

    @property
    @abstractmethod
    def _auth_headers(self) -> dict[str, str]:
        raise NotImplementedError

    @abstractmethod
    async def _request_get(self, route: str, query: dict[str, Any]) -> CommonResponse:
        raise NotImplementedError

    @abstractmethod
    async def _request_post(self, route: str,
                            payload: Union[dict[str, Any], list[Any]]) -> CommonResponse:
        raise NotImplementedError
