from src.task_management.entities import BaseTaskCase
from src.task_management.exceptions import TaskChainNotFoundError
from src.task_management.repos import TaskChain
from src.task_management.utils import get_interesting_task_chain


class TaskChainStatusesCase(BaseTaskCase):
    """
    Получение статусов цепочки заданий
    """

    async def __call__(self, slug: str) -> list[dict[str, str]]:
        task_chain: TaskChain = await get_interesting_task_chain(status=slug)
        if not task_chain:
            raise TaskChainNotFoundError
        return sorted(task_chain.task_statuses, key=lambda x: x.priority)
