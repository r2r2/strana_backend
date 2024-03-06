import asyncio
from http import HTTPMethod, HTTPStatus
from typing import Any, Coroutine

import structlog
from aiohttp import ClientSession, TCPConnector, ClientResponse, FormData, ClientError, ClientTimeout
from fastapi import UploadFile
from requests.auth import _basic_auth_str

from common.nextcloud.exceptions import NextcloudAPIError
from config import maintenance_settings, nextcloud_config, EnvTypes


class NextcloudAPI:
    """
    Интеграция с Nextcloud
    docs: https://docs.nextcloud.com/server/latest/developer_manual/client_apis/WebDAV/bulkupload.html#introduction
    """
    USER: str = nextcloud_config["username"]
    PASS: str = nextcloud_config["password"]
    SERVER: str = nextcloud_config["server"]
    REMOTE_FOLDER: str = nextcloud_config["remote_folder"]

    BULK_UPLOAD_PATH: str = "/remote.php/dav/bulk"
    UPLOAD_PATH: str = "/remote.php/webdav"

    _cached_directories: set[int] = set()  # Чтобы не создавать директории повторно

    def __init__(self, lead_id: int):
        self.lead_id: int = lead_id

        self._client_timeout: ClientTimeout = ClientTimeout(total=None, sock_connect=15, sock_read=15)
        self._session: ClientSession = self._get_session()
        self._headers = {
            'Authorization': _basic_auth_str(self.USER, self.PASS),
        }

        self._active_requests: int = 0

        self.logger: structlog.BoundLogger = structlog.get_logger(self.__class__.__name__)

        self._files_request: list[dict[str, Any]] = []

    async def add_file(self, file: UploadFile) -> str:
        """
        Загрузка файлов в Nextcloud
        """
        form_data = FormData()
        form_data.add_field(
            name='file',
            value=await file.read(),
            filename=file.filename,
            content_type=file.content_type,
        )

        file_path: str = self._get_single_upload_url(file_name=file.filename)
        request_data: dict[str, Any] = dict(
            url=file_path,
            headers=self._headers,
            data=form_data,
            method=HTTPMethod.PUT,
        )
        self._files_request.append(request_data)
        self._active_requests += 1
        return file_path

    async def upload_files(self) -> None:
        """
        Загрузка файлов в Nextcloud
        """
        if self.lead_id not in self._cached_directories:
            await self._create_directory()
            self._cached_directories.add(self.lead_id)

        await self._delete_duplicate_files()
        [
            asyncio.create_task(self._upload_file(request_data))
            for request_data in self._files_request
        ]

    async def delete_file(self, url: str) -> None:
        """
        Удаление файла
        """
        file_name: str = url.split("/")[-1]
        response: ClientResponse = await self._session.request(
            method=HTTPMethod.DELETE,
            url=url,
            headers=self._headers,
        )
        match response.status:
            case HTTPStatus.NO_CONTENT:
                self.logger.info(f'Deleted file: {file_name}')
            case _:
                self.logger.warning(f'Failed to delete file: {file_name}. Response: {await response.text()}')

    def _get_single_upload_url(self, file_name: str) -> str:
        """
        example: https://nextcloud.itstrana.site/remote.php/webdav/AMOCRM_21189697/leads/32585138/MyFile.txt
        """
        url: str = f"{self.SERVER}{self.UPLOAD_PATH}{self.REMOTE_FOLDER}{self.lead_id}/{file_name}"
        return url

    async def _upload_file(self, request_data: dict[str, Any], retries: int = 3) -> ClientResponse:
        for i in range(retries):
            try:
                response: ClientResponse = await self._session.request(**request_data)
                self.logger.info(f'Request data: {request_data}, Response status: {response.status}')
                self._active_requests -= 1
                match response.status:

                    case HTTPStatus.CREATED | HTTPStatus.OK:
                        return response

                    case HTTPStatus.NO_CONTENT:
                        self.logger.info(
                            f'File already exists', status=response.status
                        )
                        return response

                    case _:
                        self.logger.warning(
                            f'Unexpected status code: {response.status}. Response: {await response.text()}'
                        )

            except ClientError as e:
                self.logger.error(f'Request failed with exception: {e}')
                self._active_requests -= 1
                raise NextcloudAPIError
            else:
                await asyncio.sleep(1.5 ** i)
                continue
        self.logger.error(f'Request failed after {retries} retries')
        self._active_requests -= 1
        raise NextcloudAPIError

    async def _create_directory(self) -> None:
        """
        Создание директории
        example: https://nextcloud.itstrana.site/remote.php/webdav/AMOCRM_21189697/leads/99999999'
        """
        url: str = f"{self.SERVER}{self.UPLOAD_PATH}{self.REMOTE_FOLDER}{self.lead_id}"
        response: ClientResponse = await self._session.request(
            method="MKCOL",
            url=url,
            headers=self._headers,
        )
        match response.status:
            case HTTPStatus.CREATED:
                self.logger.info(f'Created directory for lead #{self.lead_id}; status={response.status}')
            case HTTPStatus.METHOD_NOT_ALLOWED:
                self.logger.info(f'Directory for lead #{self.lead_id} already exists: {await response.text()}')
            case _:
                self.logger.warning(f'Failed to create directory: {response.status=}.Response: {await response.text()}')

    async def _delete_duplicate_files(self) -> None:
        """
        Удаление файла
        """
        async_tasks: list[Coroutine | None] = [
            self.delete_file(url=file["url"])
            for file in self._files_request
        ]
        await asyncio.gather(*async_tasks)

    def _get_session(self) -> ClientSession:
        if maintenance_settings.get("environment", "dev") == EnvTypes.LOCAL:
            return ClientSession(connector=TCPConnector(verify_ssl=False), timeout=self._client_timeout)
        return ClientSession(timeout=self._client_timeout)

    async def __aenter__(self) -> "NextcloudAPI":
        """
        Nothing on entering context manager
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if not self._session.closed:
            while self._active_requests:
                await asyncio.sleep(0.1)
            await self._session.close()
