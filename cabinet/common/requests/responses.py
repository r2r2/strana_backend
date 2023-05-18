from typing import Any, Union
from aiohttp import ClientResponse
from aiographql.client import GraphQLResponse


class CommonResponse(object):
    """
    Class returned by request classes
    """

    def __init__(
        self,
        ok: bool,
        data: Any,
        status: int,
        errors: bool,
        raw: Union[GraphQLResponse, ClientResponse],
    ) -> None:
        self.ok: bool = ok
        self.data: Any = data
        self.status: int = status
        self.errors: bool = errors
        self.raw: Union[GraphQLResponse, ClientResponse] = raw
