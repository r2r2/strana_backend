from typing import Any, Callable, Coroutine, Optional

from ..entities import BaseAgentCase


class RepresesAgentsSpecsCase(BaseAgentCase):
    """
    Спеки агентов представителя агенства
    """

    def __init__(self, additional_filters: dict, group: Optional[str] = None) -> None:
        self.additional_filters: dict = additional_filters
        self.group = group or "agency_id"

    async def __call__(
        self,
        agency_id: int,
        specs: Callable[..., Coroutine],
    ) -> dict[str, Any]:
        filters: dict[str, Any] = dict(agency_id=agency_id)
        filters.update(self.additional_filters)
        result: dict[str, Any] = await specs(group=self.group, filters=filters)
        return result
