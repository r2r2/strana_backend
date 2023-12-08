from common.settings.exceptions import SystemListNotFoundError
from common.settings.repos import SystemList, SystemListRepo


async def get_system_by_slug(slug: str) -> SystemList:
    """
    Получение системы по slug
    """
    system: SystemList = await SystemListRepo().retrieve(
        filters=dict(slug=slug),
    )
    if not system:
        raise SystemListNotFoundError
    return system
