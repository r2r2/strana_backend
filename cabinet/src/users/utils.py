from typing import Any

from src.users.exceptions import UniqueStatusNotFoundError
from src.users.repos import UniqueStatus, UniqueStatusRepo


async def get_unique_status(slug: str) -> UniqueStatus:
    """
    Получаем статус закрепления по slug
    """
    status: UniqueStatus = await UniqueStatusRepo().retrieve(filters=dict(slug=slug))
    if not status:
        raise UniqueStatusNotFoundError
    return status


async def get_list_unique_status(filters: dict[str, Any]) -> list[UniqueStatus]:
    """
    Получаем список статусов закрепления
    """
    stop_check_statuses: list[UniqueStatus] = await UniqueStatusRepo().list(
        filters=filters,
    )
    return stop_check_statuses
