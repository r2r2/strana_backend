from abc import ABC
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pytz import UTC

from common.amocrm.components.interface import AmoCRMInterface
from common.requests import CommonResponse
from ..constants import AmoEntityTypes, AmoTaskTypes, AmoElementTypes
from ..types import AmoTask
import structlog

from ...sentry.utils import send_sentry_log


class AmoCRMTasks(AmoCRMInterface, ABC):
    """
    AMOCrm tasks integration
    """

    def __init__(self,
                 logger: Optional[Any] = structlog.getLogger(__name__)):
        self.logger = logger

    async def fetch_booking_tasks(self, *, booking_id: int) -> list[AmoTask]:
        """
        Получение задач, относящихся к конкретному бронированию.
        """

        route = "/tasks"
        query = {"filter[entity_id]": booking_id, "filter[entity_type]": AmoEntityTypes.LEADS}
        response = await self._request_get_v4(route=route, query=query)
        if response.data:
            return response.data["_embedded"]["tasks"]
        return []

    async def create_task(
        self,
        *,
        text: str,
        complete_till: int,
        entity_id: Optional[int] = None,
        element_id: Optional[int] = None,
        element_type: Optional[int] = None,
        entity_type: Optional[Union[AmoEntityTypes, str]] = None,
        responsible_user_id: Optional[int] = None,
        task_type: Optional[Union[AmoTaskTypes, int]] = None,
    ):
        """
        Создание задачи.

        Обязательные поля text(строка) и complete_till(unix datetime int)
        """
        route: str = "/tasks"

        payload: List[Dict[str, Any]] = dict(
            add=[
                dict(
                    element_id=element_id,
                    element_type=element_type,
                    entity_id=entity_id,
                    entity_type=entity_type,
                    complete_till=complete_till,
                    task_type_id=task_type,
                    text=text,
                    responsible_user_id=responsible_user_id,
                    is_completed=False,
                )
            ]
        )
        await self._request_post(route=route, payload=payload)

    async def _parse_tasks_data_v4(
            self,
            response: CommonResponse,
            method_name: str,
            payload: list[dict],
    ) -> list[dict]:
        """
        parse_task_data v4 api
        """
        try:
            return getattr(response, "data", {}).get("_embedded").get("tasks")
        except AttributeError as err:
            response_status = response.status
            response_data = response.data
            self.logger.warning(
                f"{method_name}: Status {response_status}: "
                f"Пришли неверные данные: {response_data}"
                f"Exception: {err}"
            )
            sentry_ctx: dict[str, Any] = dict(
                response_status=response_status,
                response_data=response_data,
                payload=payload,
            )
            await send_sentry_log(
                tag="create AMO task",
                message="Неожидаемый ответ от AMO",
                context=sentry_ctx,
            )
            return []

    async def create_task_v4(
        self,
        *,
        text: str,
        complete_till: int,
        entity_id: int | None = None,
        entity_type: AmoEntityTypes | None = None,
        responsible_user_id: int | None = None,
        task_type: AmoTaskTypes | None = None,
    ):
        """
        Создание задачи.

        Обязательные поля text(строка) и complete_till(unix datetime int)
        """
        route: str = "/tasks"
        add = dict(
            text=text,
            complete_till=complete_till,
            is_completed=False,
            created_at=int(datetime.now(tz=UTC).timestamp()),
            updated_at=int(datetime.now(tz=UTC).timestamp()),
        )

        if entity_id is not None:
            add["entity_id"] = entity_id
        if entity_type is not None:
            add["entity_type"] = entity_type
        if responsible_user_id is not None:
            add["responsible_user_id"] = responsible_user_id
        if task_type is not None:
            add["task_type"] = task_type

        payload: List[Dict[str, Any]] = [add, ]

        response = await self._request_post_v4(route=route, payload=payload)
        await self._parse_tasks_data_v4(response=response, method_name='AmoCRM.create_task_v4', payload=payload)

    async def complete_task(self, *, task_id: int, result: str) -> None:
        """
        Завершение задачи.
        """

        route: str = f"/tasks/{task_id}"
        payload = dict(result={"text": result}, is_completed=True)
        await self._request_patch_v4(route=route, payload=payload)
