from typing import Any, Callable, Coroutine

from ..entities import BaseAgentCase


class AdminsAgentsSpecsCase(BaseAgentCase):
    """
    Спеки агентов администратором
    """

    group: str = "id"

    def __init__(self, user_type: str) -> None:
        self.user_type: str = user_type

    async def __call__(self, specs: Callable[..., Coroutine]) -> dict[str, Any]:
        filters: dict[str, Any] = dict(type=self.user_type, is_deleted=False)
        result: dict[str, Any] = await specs(group=self.group, filters=filters)
        return result
