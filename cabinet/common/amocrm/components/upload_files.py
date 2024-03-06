from http import HTTPStatus

from aiohttp import ClientSession, FormData, ClientTimeout
from fastapi import UploadFile

from src.agents.exceptions import UploadDocumentInternalError
from config import amocrm_config


class AmoCRMFileUploader:
    """
    AmoCRM upload files integration
    """
    def __init__(self) -> None:
        self._url: str = amocrm_config.get("upload_url")
        self._headers: dict = dict(Referer=amocrm_config.get("url") + "/")
        self._client_timeout: ClientTimeout = ClientTimeout(total=None, sock_connect=15, sock_read=15)
        self._session: ClientSession = ClientSession(timeout=self._client_timeout)

    async def __aenter__(self) -> "AmoCRMFileUploader":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self._session.close()

    async def upload_file(self, file: UploadFile, lead_id: str) -> str:
        form = FormData()
        form.add_field("id", lead_id)
        form.add_field("type", "lead")
        form.add_field("doc", "file")
        form.add_field("file", file.file._file, filename=file.filename, content_type=file.content_type)
        async with self._session.post(url=self._url, headers=self._headers, data=form) as response:
            if response.status == HTTPStatus.OK:
                return await response.text()
            else:
                raise UploadDocumentInternalError
