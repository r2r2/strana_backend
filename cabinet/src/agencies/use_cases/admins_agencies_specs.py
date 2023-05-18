from typing import Callable, Coroutine, Any

from ..entities import BaseAgencyCase


class AdminsAgenciesSpecsCase(BaseAgencyCase):
    """
    Спеки агенств администратором
    """

    group: str = "id"

    async def __call__(self, specs: Callable[..., Coroutine]) -> dict[str, Any]:
        filters: dict[str, Any] = dict(is_deleted=False)
        result: dict[str, Any] = await specs(group=self.group, filters=filters)
        return result
