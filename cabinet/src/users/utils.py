from typing import Any

from src.users.exceptions import UniqueStatusNotFoundError, UniqueStatusButtonNotFoundError
from src.users.repos import UniqueStatus, UniqueStatusRepo, UniqueStatusButton, UniqueStatusButtonRepo


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


async def get_unique_status_button(slug: str) -> UniqueStatusButton:
    """
    Получаем кнопку статуса закрепления по slug
    """
    button: UniqueStatusButton = await UniqueStatusButtonRepo().retrieve(filters=dict(slug=slug))
    if not button:
        raise UniqueStatusButtonNotFoundError
    return button
