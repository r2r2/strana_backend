from asyncio import Future, Task, create_task, ensure_future, sleep
from base64 import b64encode
from json import dumps
from os.path import join
from types import TracebackType
from typing import Any, Optional, Type, Union

from aiofile import async_open
from aiographql.client import GraphQLClient, GraphQLResponse
from aiohttp import (ClientError, ClientResponse, ClientSession,
                     ContentTypeError, FormData, ServerDisconnectedError)
from asyncpg import Connection, connect
from config import base_dir
from fastapi import UploadFile

from ..types import IAsyncFile
from ..utils import to_snake_case
from .callbacks import exit_manager_callback
from .responses import CommonResponse


class CommonRequest:
    """
    Default request class

    Example usage:
        async with CommonRequest(**init_kwargs) as response:
            return response

    Or without context manager:
        request = CommonRequest(**init_kwargs)
        response = await request()
        await request.close()
        return response

    Or wrap it into Futures or Task objects using:
        .as_task()
        .as_future()

    Instance call returns an instance of CommonResponse class
    Which contains ok, data, status, errors and raw_response attributes
    Raw response is an instance of aiohttp.ClientResponse
    """

    _auth_type: str = "Basic"
    _retry_statuses: tuple[int] = (0, 502, 503, 504)
    _success_statuses: tuple[int] = (200, 201, 204, 301, 302)

    def __init__(
        self,
        url: str,
        method: str,
        *,
        token: Optional[str] = None,
        login: Optional[str] = None,
        timeout: Optional[int] = None,
        password: Optional[str] = None,
        auth_type: Optional[str] = None,
        max_retries: Optional[int] = None,
        backoff: Optional[float] = None,
        backoff_max: Optional[float] = None,
        query: Optional[dict[str, Any]] = None,
        session: Optional[ClientSession] = None,
        payload: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
        files: Optional[dict[str, list[IAsyncFile]]] = None,
        headers: Optional[dict[str, Any]] = None,
    ) -> None:
        self._ok: Optional[bool] = None
        self._retries: int = 0
        self._backoff_time: float = 0
        self._status: Optional[int] = None
        self._current_status: Optional[int] = None
        self._response: Optional[CommonResponse] = None
        self._raw_response: Optional[ClientResponse] = None
        self._retry_response: Optional[ClientResponse] = None
        self._data: Union[str, dict[str, Any], None] = None

        self._url: str = url
        self._method: str = method.lower()
        self._payload: Union[dict[str, Any], None] = payload
        self._json: Optional[dict[str, Any]] = json
        self._files = files

        self._timeout: int = timeout if timeout else 20
        self._max_retries: int = max_retries if max_retries else 20
        self._backoff: float = backoff if backoff else 0.1
        self._backoff_max: float = backoff_max if backoff_max else 0.5
        self._session: ClientSession = session if session else ClientSession()
        self._headers: Union[dict[str, Any], None] = headers if headers else {}

        if auth_type:
            assert auth_type and token, "auth_type argument requires token implementation."
            self._auth_type: str = auth_type if auth_type else self._auth_type

        if token:
            self._authorization: str = f"{self._auth_type} {token}"
            self._headers["Authorization"]: str = self._authorization

        if login and password:
            self._authorization: str = (
                f"{self._auth_type} "
                f"{b64encode(f'{login}:{password}'.encode('utf-8')).decode('utf-8')}"
            )
            self._headers["Authorization"]: str = self._authorization

        if query:
            self._url += "?"
            for key, value in query.items():
                self._url += f"{key}={value}&"
            self._url: str = self._url[:-1]

    def as_future(self) -> Future:
        """
        Wraps to a future object and returns an asyncio.Future instance
        """
        future_request: Future = ensure_future(self())
        future_request.add_done_callback(exit_manager_callback(request=self))
        return future_request

    def as_task(self) -> Task:
        """
        Wraps to a task object and return an asyncio.Task instance
        """
        task_request: Task = create_task(self())
        task_request.add_done_callback(exit_manager_callback(request=self))
        return task_request

    async def __aenter__(self) -> CommonResponse:
        """
        Executing request on entering context manager
        """
        return await self()

    async def __call__(self) -> CommonResponse:
        """
        Request execution
        """
        if not self._response:
            self._raw_response = await self._make_request()
            self._response: CommonResponse = CommonResponse(
                ok=await self.ok,
                data=await self.data,
                status=await self.status,
                errors=self.errors,
                raw=self._raw_response,
            )
        return self._response

    @property
    async def ok(self) -> Optional[bool]:
        """
        Is response ok defined by status
        """
        if self._ok is None and self._raw_response:
            self._ok: bool = self._raw_response.ok
        return self._ok

    @property
    async def data(self) -> Union[str, dict[str, Any], None]:
        """
        Extracting data from response
        """
        if not self._data and self._raw_response:
            if 'json' in self._raw_response.content_type:
                self._data: dict[str, Any] = await self._raw_response.json()
            elif 'docx' in self._raw_response.content_type:
                self._data: bytes = await self._raw_response.read()
            else:
                self._data: str = await self._raw_response.text("utf-8", errors='ignore')
        return self._data

    @property
    async def status(self) -> Optional[int]:
        """
        Extracting status from executed request
        """
        if self._status is None and self._raw_response:
            self._status: int = self._raw_response.status
        return self._status

    @property
    def errors(self) -> bool:
        """
        No errors in common request, always false
        """
        return False

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """
        Closing connections on exiting context manager
        """
        await self.close()

    async def close(self) -> None:
        """
        Closing session and response streaming
        """
        if not self._session.closed:
            await self._session.close()
        if not self._raw_response.closed:
            self._raw_response.close()

    async def _make_request(self) -> ClientResponse:
        """make_request"""
        if not self._raw_response:
            request_options = await self._make_request_options()
            try:
                response: ClientResponse = await getattr(self._session, self._method)(
                    **request_options
                )
                self._current_status: int = response.status
                if self._current_status in self._retry_statuses:
                    response.raise_for_status()
            except ClientError as e:
                print("ClientError: ", e)
                response: ClientResponse = await self._retry(request_options)
            self._raw_response: ClientResponse = response
        return self._raw_response

    async def _retry(self, request_options: dict[str, Any]) -> ClientResponse:
        """retry"""
        self._retries += 1
        self._backoff_time = self._backoff
        self._backoff_time = self._backoff_time if self._backoff_time < self._backoff_max else self._backoff_max
        await sleep(self._backoff_time)
        try:
            self._retry_response: ClientResponse = await getattr(self._session, self._method)(
                **request_options
            )
            self._current_status: int = self._retry_response.status
            if self._retries < self._max_retries:
                self._retry_response.raise_for_status()
        except ClientError:
            if self._retries < self._max_retries and self._current_status in self._retry_statuses:
                await self._retry(request_options)
        return self._retry_response

    async def _make_form_data(self) -> FormData:
        """make_form_data"""
        form_data = FormData()
        for field_name, field_value in self._payload.items():
            form_data.add_field(field_name, field_value)
        for file_category, category_files in self._files.items():
            file: UploadFile
            for file in category_files:
                form_data.add_field(
                    file_category, await file.read(), content_type=file.content_type, filename=file.filename
                )
        return form_data

    async def _make_request_options(self) -> dict:
        """make_request_options"""
        request_options: dict[str, Any] = dict(
            url=self._url, timeout=self._timeout, headers=self._headers
        )
        if self._files:
            request_options["data"] = await self._make_form_data()
        elif self._payload:
            request_options["data"] = dumps(self._payload)
        elif self._json:
            request_options["json"] = self._json
        return request_options


class GraphQLRequest:
    """
    Graphql request class

    Example usage:
        async with GraphQLRequest(**init_kwargs) as response:
            return response

    Or without context manager:
        request = GraphQLRequest(**init_kwargs)
        response = await request()
        await request.close()
        return response

    Or wrap it into Futures or Task objects using:
        .as_task()
        .as_future()

    Instance call returns an instance of CommonResponse class
    Which contains ok, data, status, errors and raw_response attributes
    Raw response is an instance of aiographql.client.GraphQLResponse
    Data keys are transformed recursively to snake_case representation
    """

    _auth_type: str = "Basic"
    _default_headers: dict[str, str] = {"Content-Type": "application/json"}

    def __init__(
        self,
        url: str,
        type: str,  # pylint: disable=redefined-builtin
        query_name: str,
        query_directory: str,
        *,
        login: Optional[str] = None,
        timeout: Optional[int] = None,
        password: Optional[str] = None,
        max_retries: Optional[int] = None,
        backoff: Optional[float] = None,
        backoff_max: Optional[float] = None,
        session: Optional[ClientSession] = None,
        headers: Optional[dict[str, Any]] = None,
        filters: Optional[Union[str, tuple[str]]] = None,
    ) -> None:
        self._ok: bool = None
        self._retries: int = 0
        self._backoff_time: float = 0
        self._query: str = None
        self._errors: bool = None
        self._response: CommonResponse = None
        self._raw_response: GraphQLResponse = None
        self._data: Union[list[Any], dict[str, Any]] = None

        self._url: str = url
        self._type: str = type
        self._query_name: str = query_name
        self._query_directory: str = query_directory
        self._retry_response: GraphQLResponse = None
        self._filters: Union[list[str], tuple[str], str, None] = filters

        self._timeout: int = timeout if timeout else 20
        self._max_retries: int = max_retries if max_retries else 20
        self._backoff: float = backoff if backoff else 0.2
        self._backoff_max: float = backoff_max if backoff_max else 5
        self._session: ClientSession = session if session else ClientSession()
        self._headers: Union[dict[str, Any], None] = headers if headers else self._default_headers

        if login and password:
            self._authorization: str = (
                f"{self._auth_type} "
                f"{b64encode(f'{login}:{password}'.encode('utf-8')).decode('utf-8')}"
            )
            self._headers["Authorization"]: str = self._authorization

    def as_future(self) -> Future:
        """
        Wraps to a future object and returns an asyncio.Future instance
        """
        future_request: Future = ensure_future(self())
        future_request.add_done_callback(exit_manager_callback(request=self))
        return future_request

    def as_task(self) -> Task:
        """
        Wraps to a task object and return an asyncio.Task instance
        """
        task_request: Task = create_task(self())
        task_request.add_done_callback(exit_manager_callback(request=self))
        return task_request

    async def __aenter__(self) -> CommonResponse:
        """
        Executing request on entering context manager
        """
        return await self()

    async def __call__(self) -> CommonResponse:
        """
        Request execution
        """
        if self._response:
            response: CommonResponse = self._response
        else:
            self._response: CommonResponse = CommonResponse(
                ok=await self.ok,
                data=await self.data,
                status=self.status,
                errors=await self.errors,
                raw=self._raw_response,
            )
            response: CommonResponse = self._response
        return response

    @property
    async def ok(self) -> bool:
        """
        Is response ok defined by ok field in it
        """
        if self._ok is not None:
            ok: bool = self._ok
        else:
            data: Union[list[Any], dict[str, Any], None] = await self.data
            if data:
                self._ok: bool = bool(data.get("ok"))
            else:
                self._ok: bool = False
            ok: bool = self._ok
        return ok

    @property
    async def data(self) -> Union[list[Any], dict[str, Any], None]:
        """
        Extracting data from response and transforming recursively to snake case
        """
        if self._data:
            data: Union[list[Any], dict[str, Any]] = self._data
        else:
            response: GraphQLResponse = await self._make_request()
            data: Optional[Union[list, dict[str, Any]]] = None
            try:
                data: Union[list[Any], dict[str, Any]] = response.json["data"][self._type]
            except (KeyError, AttributeError):
                pass

            if isinstance(data, dict):
                self._data: dict[str, Any] = self._to_snake_case(data)
            elif isinstance(data, list):
                self._data: list[Any] = []
                for _object in data:
                    self._data.append(self._to_snake_case(_object))
            else:
                self._data = None
            data: Union[list[Any], dict[str, Any], None] = self._data
        return data

    @property
    async def errors(self) -> bool:
        """
        Checking response data for errors
        """
        if self._errors is not None:
            errors: bool = self._errors
        else:
            response: GraphQLResponse = await self._make_request()
            data: dict[str, Any] = response.json
            self._errors: bool = "errors" in data
            errors: bool = self._errors
        return errors

    @property
    def status(self) -> int:
        """
        No bad statuses in graphql request
        """
        return 200

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """
        Closing connections on exiting context manager
        """
        await self.close()

    async def close(self) -> None:
        """
        Closing session streaming
        """
        if not self._session.closed:
            await self._session.close()

    async def _make_request(self) -> GraphQLResponse:
        """
        Making request
        """
        if self._raw_response:
            response: GraphQLResponse = self._raw_response
        else:
            client: GraphQLClient = GraphQLClient(
                endpoint=self._url, session=self._session, headers=self._headers
            )
            query: str = await self._get_query()
            try:
                self._raw_response: GraphQLResponse = await client.query(query % self._filters)
                raise ServerDisconnectedError
            except (ServerDisconnectedError, ContentTypeError):
                self._raw_response: GraphQLResponse = await self._retry(client=client)
            response: GraphQLResponse = self._raw_response
        return response

    async def _retry(self, client: GraphQLClient) -> GraphQLResponse:
        """retry"""
        self._retries += 1
        self._backoff_time += self._backoff
        self._backoff_time = self._backoff_time if self._backoff_time < self._backoff_max else self._backoff_max
        await sleep(self._backoff_time)
        try:
            query: str = await self._get_query()
            self._retry_response: GraphQLResponse = await client.query(query % self._filters)
        except (ServerDisconnectedError, ContentTypeError):
            if self._retries < self._max_retries:
                await self._retry(client=client)
        return self._retry_response

    async def _get_query(self) -> str:
        """get_query"""
        if self._query:
            query: str = self._query
        else:
            query_directory: str = join(base_dir + self._query_directory, self._query_name)
            async with async_open(query_directory, "r") as file:
                self._query: str = await file.read()
                query: str = self._query
        return query

    def _to_snake_case(self, data: dict[str, Any]) -> dict[str, Any]:
        """to_snake_case"""
        new_data: dict[str, Any] = {}
        for field, value in data.items():
            if isinstance(value, dict):
                new_data[to_snake_case(field)]: dict[str, Any] = self._to_snake_case(value)
            else:
                new_data[to_snake_case(field)]: Any = value
            if field == "id":
                new_data["global_id"]: str = value
        new_data.pop("id", None)
        return new_data


class UpdateSqlRequest:
    """
    Update sql request
    """

    def __init__(
        self,
        table: str,
        data: dict[str, Any],
        filters: dict[str, Any],
        connection_options: dict[str, Any],
    ) -> None:
        self._connection: Union[Connection, None] = None

        self._table: str = table
        self._data: dict[str, Any] = data
        self._filters: dict[str, Any] = filters
        self._connection_options: dict[str, Any] = connection_options

    async def __aenter__(self) -> str:
        """
        Executing logic on entering context manager
        """
        self._connection: Connection = await connect(**self._connection_options)
        return await self()

    async def __call__(self) -> str:
        """
        Update execution
        """
        return await self._connection.execute(query=self._get_query())

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """
        Closing connection on exiting context manager
        """
        await self._connection.close()

    def _get_query(self) -> str:
        """
        Query building
        """
        query: str = f"{self._get_update()}{self._get_set()}{self._get_where()}"
        return query

    def _get_update(self) -> str:
        """
        Update building
        """
        update: str = f"UPDATE {self._table} "
        return update

    def _get_set(self) -> str:
        """
        Full set buildings
        """
        if len(self._data) == 1:
            _set: str = str()
            for field, value in self._data.items():
                _set += f"SET {field} = '{value}'"
        else:
            fields: str = str()
            values: str = str()
            for field, value in self._data.items():
                fields += f"{field}, "
                values += f"'{value}', "
            fields: str = fields[:-2]
            values: str = values[:-2]
            _set: str = f"SET ({fields}) = ({values}) "
        return _set

    def _get_where(self) -> str:
        """
        Full where building
        """
        filters: str = str()
        for field, value in self._filters.items():
            filters += f"{field} = {value} AND "
        where: str = f"WHERE {filters}"[:-4]
        return where
