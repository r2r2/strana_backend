from abc import ABC
from typing import Optional, List, Dict, Any, Union

from common.amocrm.components.interface import AmoCRMInterface
from ..constants import AmoEntityTypes, AmoTaskTypes, AmoElementTypes
from ..types import AmoTask


class AmoCRMTasks(AmoCRMInterface, ABC):
    """
    AMOCrm tasks integration
    """

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

    async def complete_task(self, *, task_id: int, result: str) -> None:
        """
        Завершение задачи.
        """

        route: str = f"/tasks/{task_id}"
        payload = dict(result={"text": result}, is_completed=True)
        await self._request_patch_v4(route=route, payload=payload)
