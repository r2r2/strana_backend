import io
from datetime import datetime
from types import TracebackType
from typing import Any, Callable, Coroutine, Optional, Type, Union

import structlog
from aiohttp import ClientSession
from common.amocrm.exceptions import AmocrmHookError
from config import getdoc_settings
from fastapi import UploadFile

from ..requests import CommonRequest, CommonResponse
from ..wrappers import mark_async
from .interface import GetDocInterface
from .types import EntityTypes, ExtensionTypes, GetdocResponse


@mark_async
class GetDoc(GetDocInterface):
    _default_headers: dict[str, str] = {"Content-Type": "application/x-www-form-urlencoded"}

    async def __ainit__(self) -> None:
        self.logger: Optional[Any] = structlog.getLogger(__name__)
        self._session: ClientSession = ClientSession()
        self._request_class: Type[CommonRequest] = CommonRequest
        self._url: str = getdoc_settings["url"]

    async def __aenter__(self) -> "GetDoc":
        """
        Nothing on entering context manager
        """
        return self

    async def __aexit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType],
    ) -> None:
        """
        Closing session on exiting context manager
        """
        if not self._session.closed:
            await self._session.close()
        if exc_val and exc_type:
            raise AmocrmHookError(reason=f'{exc_type.__name__}: {exc_val}')

    @property
    def _auth_query(self) -> dict[str, Any]:
        return dict(
            amo_domain=getdoc_settings['amo_domain'],
            account_id=getdoc_settings['account_id'],
            user_id=getdoc_settings['user_id'],
        )

    async def _request_post(self, payload: Union[dict[str, Any], list[Any]]) -> CommonResponse:
        request_options: dict[str, Any] = self._post_options(payload)
        request_post: Callable[..., Coroutine] = self._request_class(**request_options)
        response: CommonResponse = await request_post()
        return response

    async def _request_get(self, url: str) -> CommonResponse:
        request_options: dict[str, Any] = dict(url=url, method='GET', session=self._session)
        request_get: Callable[..., Coroutine] = self._request_class(**request_options)
        response: CommonResponse = await request_get()
        return response

    def _post_options(self, payload: dict[str, Any]) -> dict[str, Any]:
        return dict(
            method="POST",
            payload=payload,
            files=dict(file=[]),
            query=self._auth_query,
            url=self._url,
            session=self._session,
            headers=self._default_headers,
            timeout=300,
        )

    async def get_doc(self, lead_id: int, template: str, contact_id: Optional[int] = None) -> UploadFile:
        """
        Получение документа из GetDoc
        """
        payload: dict[str, Any] = dict(
            lead_id=lead_id,
            filename=template,
            entity=EntityTypes.leads,
            extension=ExtensionTypes.docx,
            user_name="Интеграции Digital",
            user_id=getdoc_settings['user_id'],
            contact_id=contact_id,
        )
        response: CommonResponse = await self._request_post(payload=payload)
        getdoc = GetdocResponse.parse_obj(response.data)
        if not getdoc.success:
            self.logger.error(f'GetDoc response has no data: {response.data}')
            raise AmocrmHookError(reason=f'GetDoc response has no data: {getdoc.error}')
        filename = f"{getdoc.data.name} {datetime.fromtimestamp(getdoc.data.created_at).strftime('%Y-%m-%d %H:%M')}" \
                   f".{getdoc.data.filename.split('.')[-1]}"
        print("GetDoc Response: ", getdoc)
        data: CommonResponse = await self._request_get(getdoc.data.url)
        return UploadFile(filename=filename, file=io.BytesIO(data.data))
