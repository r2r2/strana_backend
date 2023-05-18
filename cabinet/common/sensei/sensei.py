from http import HTTPStatus

from aiohttp import ClientSession, TCPConnector

from config import sensei_config, maintenance_settings


class SenseiAPI:
    """
    Интеграция Sensei API
    """

    _auth_headers: dict[str, str] = {"X-Auth-Sensei-Token": sensei_config.get("secret")}
    SENSEI_PID: int = sensei_config.get("sensei_pid")

    def __init__(self) -> None:
        self._session: ClientSession = ClientSession(
            connector=TCPConnector(verify_ssl=False)
        ) if maintenance_settings.get("environment", "dev") else ClientSession()
        self._url: str = sensei_config.get("url") + sensei_config.get("api_route")

    async def __aenter__(self) -> 'SenseiAPI':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if not self._session.closed:
            await self._session.close()

    async def process_list(self):
        """
        Получение списка процессов
        """
        route_url: str = "process/list/"
        async with self._session.get(url=self._url + route_url, headers=self._auth_headers) as response:
            if response.status == HTTPStatus.OK:
                return await response.json()

    async def process_start(self, process_id: int, amocrm_id: int):
        """
        Запуск процесса
        process_id: ID процесса
        amocrm_id: ID сделки
        entity_data: [
            {"entity_id": 30188325, "entity_type":1},
            {"entity_id": 30188323, "entity_type":1},
        ]
            entity_id: в данных означает ID сделки.
            entity_type: будет означать тип сущности, с которым мы работаем (отличается от ID сущностей amoCRM).
            Для нас это всегда сделка и потому entity_type всегда равен 1
        """
        entity_data: dict[str:list] = dict(
            data=[
                dict(entity_id=amocrm_id, entity_type=1)
            ]
        )
        route_url: str = f"process/start/{process_id}"
        async with self._session.post(
                url=self._url + route_url, headers=self._auth_headers, json=entity_data
        ) as response:
            if response.status == HTTPStatus.OK:
                return await response.json()

    async def process_list_start(self, process_id: int, amocrm_ids: list[int]):
        """
        Запуск процесса для списка сделок
        process_id: ID процесса
        amocrm_ids: список ID сделок
        """
        entity_data: dict[str:list] = dict(data=self._get_entity_data(amocrm_ids))
        route_url: str = f"process/start/{process_id}"
        async with self._session.post(
                url=self._url + route_url, headers=self._auth_headers, json=entity_data
        ) as response:
            if response.status == HTTPStatus.OK:
                return await response.json()

    async def process_start_add(self, process_id: int, amocrm_id: int, name: str, phone: str, email: str):
        """
        Запуск процесса с заданными локальными параметрами
        process_id: ID процесса
        amocrm_id: ID сделки
        При отправке таких запросов важно, чтобы в процессе уже был создан указанный параметр.
        Запрос с несуществующими параметрами не будет выполнен.
        """
        entity_data: dict[str:list] = dict(
            data=[
                dict(entity_id=amocrm_id, entity_type=1)
            ],
            param_values=self._parse_params(name=name, phone=phone, email=email)
        )
        route_url: str = f"process/start/{process_id}"
        async with self._session.post(
                url=self._url + route_url, headers=self._auth_headers, json=entity_data
        ) as response:
            if response.status == HTTPStatus.OK:
                return await response.json()

    async def task_close(self, amocrm_id: int, task_id: int, result: str):
        """
        Завершение задачи с заданным результатом
        amocrm_id: ID сделки
        task_id: ID задачи
        result: Результат закрытия задачи, например "Перезвонить"
        """
        data: dict = dict(
            entity_id=amocrm_id,
            entity_type=1,
            result_caption=result,
            task_id=task_id
        )
        route_url: str = "element/task/complete"
        async with self._session.post(
                url=self._url + route_url, headers=self._auth_headers, json=data
        ) as response:
            if response.status == HTTPStatus.OK:
                return await response.json()

    async def tasks_close(self, process_id: int, amocrm_ids: list[int], close_tasks=True):
        """
        Завершение процессов и задач по ним
        process_id: ID процесса
        amocrm_ids: список ID сделок
        close_tasks: bool = True (указывать не обязательно).
        Он означает, что в указанных сделках помимо завершения процесса, также будет завершена задача по процессу
        """
        entity_data: dict[str:list] = dict(close_tasks=close_tasks, data=self._get_entity_data(amocrm_ids))
        route_url: str = f"process/stop/{process_id}"
        async with self._session.post(
                url=self._url + route_url, headers=self._auth_headers, json=entity_data
        ) as response:
            if response.status == HTTPStatus.OK:
                return await response.json()

    async def lead_process_close(self, process_id: int, amocrm_id: int, close_tasks=True):
        """
        Завершение всех процессов в сделке
        process_id: ID процесса
        amocrm_ids: ID сделки
        close_tasks: bool = True (указывать не обязательно).
        Этот метод требуется для завершения всех процессов и задач по ним внутри одной сделкию
        """
        entity_data: dict[str:list] = dict(
            close_tasks=close_tasks,
            data=[
                dict(entity_id=amocrm_id, entity_type=1)
            ]
        )
        route_url: str = f"process/stop-entity/{process_id}"
        async with self._session.post(
                url=self._url + route_url, headers=self._auth_headers, json=entity_data
        ) as response:
            if response.status == HTTPStatus.OK:
                return await response.json()

    def _get_entity_data(self, amocrm_ids: list[int]) -> list:
        entity_list: list = [dict(entity_id=amocrm_id, entity_type=1) for amocrm_id in amocrm_ids]
        return entity_list

    def _parse_params(self, name: str, phone: str, email: str) -> dict:
        """
        name: Имя и Фамилия
        phone: номер телефона
        email: почта
        """
        param_values: dict = dict(
            local=[
                {"name": "name", "value": name},
                {"name": "phone", "value": phone},
                {"name": "email", "value": email}
            ]
        )
        return param_values
