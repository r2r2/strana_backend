from collections import defaultdict
from datetime import datetime
from typing import Any
from urllib.parse import urlencode

from aiohttp import ClientSession, TCPConnector

from config import maintenance_settings, amocrm_config


class AmoCRMAvailableMeetingSlots:
    """
    Получение доступных слотов для записи на встречу
    """
    _get_slots_from_amo_url: str = amocrm_config.get("widget_aquire_url")
    _headers: dict[str, str] = {"Referer": amocrm_config.get("url") + "/"}

    def __init__(self):
        self._session: ClientSession = ClientSession(
            connector=TCPConnector(verify_ssl=False)
        ) if maintenance_settings.get("environment", "dev") else ClientSession()

    async def __call__(self, *, payload: dict[str: Any]) -> list[dict[str: Any]]:
        query_params: str = urlencode(payload, doseq=False)
        url: str = f"{self._get_slots_from_amo_url}?{query_params}"
        async with self._session.get(url=url, headers=self._headers) as response:
            if response.status == 200:
                return self._transform_response(await response.json())

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