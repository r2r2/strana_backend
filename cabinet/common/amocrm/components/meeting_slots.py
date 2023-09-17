from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Optional, Type
from urllib.parse import urlencode

from aiohttp import ClientSession, TCPConnector

from config import maintenance_settings, amocrm_config
from src.cities.repos import City, CityRepo
from src.projects.repos import ProjectRepo, Project


class AmoCRMAvailableMeetingSlots:
    """
    Получение доступных слотов для записи на встречу
    """
    _get_slots_from_amo_url: str = amocrm_config.get("widget_aquire_url")
    _headers: dict[str, str] = {"Referer": amocrm_config.get("url") + "/"}
    _time_slot: list[str] = [
        "10:00:00",
        "11:00:00",
        "12:00:00",
        "13:00:00",
        "14:00:00",
        "15:00:00",
        "16:00:00",
        "17:00:00",
        "18:00:00"
    ]

    def __init__(
            self,
            project_repo: Type[ProjectRepo],
            city_repo: Type[CityRepo],
    ):
        self.project_repo = project_repo()
        self.city_repo = city_repo()
        self._session: ClientSession = ClientSession(
            connector=TCPConnector(verify_ssl=False)
        ) if maintenance_settings.get("environment", "dev") else ClientSession()

    async def __call__(self, city_slug: str, meet: list[str], project_id: Optional[int] = None) -> list[dict[str: Any]]:
        if project_id:
            project: Project = await self.project_repo.retrieve(filters=dict(id=project_id))
            city: City = await self.city_repo.retrieve(filters=dict(slug=city_slug))
            payload: dict[str: Any] = dict(city=city.name, obj=project.name, meet=meet)
            if payload.get("obj"):query_params: str = urlencode(payload, doseq=False)
            url: str = f"{self._get_slots_from_amo_url}?{query_params}"
            async with self._session.get(url=url, headers=self._headers) as response:
                if response.status == 200:
                    return self._transform_response(await response.json())
        else:
            start_day = datetime.today() + timedelta(days=1)
            day_list = [start_day + timedelta(days=x) for x in range(31)]
            available_slots = []
            for day in day_list:
                slot: dict[str, str] = dict(date=day.strftime("%Y-%m-%d"), times=self._time_slot)
                available_slots.append(slot)
            return available_slots

    def _transform_response(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Преобразование ответа от API в удобный для фронта формат
        """
        grouped_data = defaultdict(list)

        for item in response['data']:
            date_time_obj = datetime.fromisoformat(item['time'])
            date_ = date_time_obj.date().isoformat()
            time = date_time_obj.time().isoformat()

            grouped_data[date_].append(time)

        transformed_data = [{'date': date_, 'times': times} for date_, times in grouped_data.items()]

        return transformed_data
