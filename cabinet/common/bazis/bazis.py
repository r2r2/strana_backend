# pylint: disable=broad-except

from datetime import date, datetime
from enum import Enum
from types import TracebackType
from typing import Literal, Optional, Type, TypedDict

import sentry_sdk
from aiohttp import ClientSession
from common.requests import CommonRequest
from common.types import IAsyncFile
from common.wrappers import mark_async
from config import bazis_config


class BazisInputDocuments(TypedDict, total=False):
    """Входные данные для распознавания документов в БАЗИС-е."""

    passport_first_image: IAsyncFile


class BazisOutputDocuments(TypedDict):
    """Выходные данные проверки распознавания документов в БАЗИС-е."""

    passport_serial: Optional[str]
    passport_number: Optional[str]
    passport_issued_by: Optional[str]
    passport_department_code: Optional[str]
    passport_issued_date: Optional[date]

    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]

    passport_birth_date: Optional[date]
    passport_birth_place: Optional[str]
    passport_gender: Optional[Literal["male", "female"]]


class BazisCheckDocumentsReason(int, Enum):
    """Ответ БАЗИС-а на запрос проверки завершённости задачи распознавания документов."""

    success = 0
    task_not_found = 1
    failed = 2
    documents_are_still_recognizing = 3


class TokenRequest(TypedDict):
    email: str
    password: str


class TokenResponse(TypedDict):
    token: str


class CreateTaskDataPayload(TypedDict):
    preset: str


class CreateTaskFilesPayload(TypedDict):
    files: list[IAsyncFile]


class _UploadedFile(TypedDict):
    path: str
    downloadUrl: str
    size: int
    originalFileName: str
    checksum: str
    id: None


class CreateTaskResponse(TypedDict):
    id: str
    creatorId: str
    documentType: str
    solution: dict
    filesUploaded: list[_UploadedFile]
    preset: str

    # Completed - распознавание завершено
    # Pending - распознавание в процессе
    # Rejected - ошибка распознавания
    status: Literal["Completed", "Pending", "Rejected"]


class _Passport(TypedDict):
    gender: str  # "МУЖ."
    issuer: str  # "ОТДЕЛОМ ВНУТРЕННИХ ДЕЛ ОКТЯБРЬСКОГО ОКРУГА ГОРОДА АРХАНГЕЛЬСКА"
    number: str  # "000000"
    series: str  # "1104"
    present: bool  # true
    lastName: str  # "ИМЯРЕК"
    birthDate: str  # "12.09.1682"
    firstName: str  # "ЕВГЕНИЙ"
    issueDate: str  # "17.12.2004"
    birthPlace: str  # "ГОР. АРХАНГЕЛЬСК"
    issuerCode: str  # "292-000"
    middleName: str  # "АЛЕКСАНДРОВИЧ"


class _Explained(TypedDict):
    passport: _Passport


class _Solution(TypedDict):
    explained: _Explained


class CheckTaskResponse(TypedDict):
    id: str
    creatorId: str
    documentType: str
    status: Literal["Completed", "Pending", "Rejected"]
    solution: _Solution


@mark_async
class Bazis:
    """Сервис БАЗИС. Распознаёт данные с фотограций паспорта, инн и т.п."""

    COMPLETED_STATUS = "Completed"

    async def __ainit__(self) -> None:
        self._session: ClientSession = ClientSession()
        self._request_class = CommonRequest
        self._bazis_url = bazis_config["url"]
        self._bazis_username = bazis_config["username"]
        self._bazis_password = bazis_config["password"]
        self._preset = "mortgage.pilot"

    async def __aenter__(self) -> "Bazis":
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

    async def upload_files(self, files: BazisInputDocuments) -> str:
        """Загрузка документов в БАЗИС для распознавания.

        Возвращается task_id, по которому можно поллить бэкенд, который поллит базис,
        на предмет статуса обработки данных паспорта.
        """
        token: str = await self._get_token()
        payload: CreateTaskDataPayload = {"preset": self._preset}
        files_payload: CreateTaskFilesPayload = {"files": [files["passport_first_image"]]}
        request = self._request_class(
            url=self._create_task_url,
            method="POST",
            timeout=10000,
            max_retries=5,
            payload=payload,
            files=files_payload,
            auth_type="Bearer",
            token=token,
            session=self._session,
        )

        response = await request()
        data: CreateTaskResponse = response.data
        return data["id"]

    async def check_documents(
        self, task_id: str
    ) -> tuple[Optional[BazisOutputDocuments], BazisCheckDocumentsReason]:
        """Проверить в Базисе, распознались ли документы.

        Если распознались, вернутся данные распозннанных документов.
        """
        token: str = await self._get_token()
        request = self._request_class(
            url=self._check_task_url(task_id),
            method="GET",
            timeout=10000,
            max_retries=5,
            auth_type="Bearer",
            token=token,
            session=self._session,
        )

        response = await request()
        # Задача с указанным id не найдена
        if response.status == 404:
            return None, BazisCheckDocumentsReason.task_not_found

        data: CheckTaskResponse = response.data
        try:
            completed = data["status"] == self.COMPLETED_STATUS
        except Exception as exception:
            sentry_sdk.capture_exception(exception)
            return None, BazisCheckDocumentsReason.failed

        # БАЗИС ещё не успел распознать документы
        if not completed:
            return None, BazisCheckDocumentsReason.documents_are_still_recognizing

        # Пользователь отправил не паспорт
        try:
            passport_presents = data["solution"]["explained"]["passport"]["present"]
        except Exception:
            passport_presents = False

        if not passport_presents:
            return None, BazisCheckDocumentsReason.failed

        # Успешно распознано, парсим
        try:
            parsed_data = self._parse_passport_data(data)
            return parsed_data, BazisCheckDocumentsReason.success
        except Exception as exception:
            sentry_sdk.capture_exception(exception)
            return None, BazisCheckDocumentsReason.failed

    @property
    def _token_url(self) -> str:
        """URL получения токена авторизации."""
        return f"{self._bazis_url}access-tokens"

    @property
    def _create_task_url(self) -> str:
        """URL создания задачи распознавания документов."""
        return f"{self._bazis_url}tasks"

    def _check_task_url(self, task_uuid: str) -> str:
        """URL проверки задачи распознавания документов."""
        return f"{self._bazis_url}tasks/{task_uuid}"

    async def _get_token(self) -> str:
        """Получение токена авторизации БАЗИС."""
        json_data: TokenRequest = {"email": self._bazis_username, "password": self._bazis_password}
        request = self._request_class(
            url=self._token_url,
            method="POST",
            timeout=10,
            max_retries=5,
            json=json_data,
            session=self._session,
        )

        response = await request()
        data: TokenResponse = response.data
        try:
            return data["token"]
        except Exception as exception:
            sentry_sdk.capture_exception(exception)
            raise exception

    @staticmethod
    def _parse_passport_data(task_data: CheckTaskResponse) -> BazisOutputDocuments:
        """
        parse_passport_data
        """
        passport_data = task_data["solution"]["explained"]["passport"]

        passport_issued_date: Optional[date] = (
            datetime.strptime(passport_data["issueDate"], "%d.%m.%Y").date()
            if passport_data.get("issueDate", None) is not None
            else None
        )
        passport_birth_date: Optional[date] = (
            datetime.strptime(passport_data["birthDate"], "%d.%m.%Y").date()
            if passport_data.get("birthDate", None) is not None
            else None
        )
        passport_number: Optional[str] = (
            "{} {}".format(passport_data["number"][0:3], passport_data["number"][3:6])
            if passport_data.get("number", None) is not None
            else None
        )
        passport_gender: Optional[Literal["male", "female"]] = None
        if passport_data.get("gender", None) is not None:
            if passport_data["gender"] == "МУЖ.":
                passport_gender = "male"
            else:
                passport_gender = "female"

        output_documents: BazisOutputDocuments = {
            "passport_serial": passport_data.get("series", None),
            "passport_number": passport_number,
            "passport_issued_by": passport_data.get("issuer", None),
            "passport_department_code": passport_data.get("issuerCode", None),
            "passport_issued_date": passport_issued_date,
            "name": passport_data.get("firstName", None),
            "surname": passport_data.get("lastName", None),
            "patronymic": passport_data.get("middleName", None),
            "passport_birth_date": passport_birth_date,
            "passport_birth_place": passport_data.get("birthPlace", None),
            "passport_gender": passport_gender,
        }
        return output_documents
