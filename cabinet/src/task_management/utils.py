from typing import Any, Generator, Optional

from src.amocrm.repos import AmocrmStatus
from src.task_management.repos import TaskInstance


def build_task_data(
        task_instances: list[TaskInstance],
        booking_status: Optional[AmocrmStatus] = None,
) -> Generator[dict[str, Any], None, None]:
    """
    Сборка данных для отображения задач
    """
    if booking_status is None:
        return
    for task_instance in task_instances:
        task_visibility = task_instance.status.tasks_chain.task_visibility
        if booking_status not in task_visibility:
            continue
        task_data = {
            "type": task_instance.status.type.value,
            "title": task_instance.status.name,
            "text": task_instance.status.description,
            "hint": task_instance.comment,
            "buttons": _build_buttons(task_instance),
        }
        yield task_data


def _build_buttons(task_instance: TaskInstance) -> Optional[list[dict[str, Any]]]:
    """
    Сборка кнопок для задачи.
    Чем меньше приоритет - тем выше кнопка выводится в задании.
    Если приоритет не указан, то кнопка выводится в конце списка.
    """
    if not task_instance.status.button:
        return []
    sorted_buttons = sorted(task_instance.status.button, key=lambda b: (b.priority is None, b.priority))
    buttons = [{
        "label": button.label,
        "type": button.style.value,
        "action": {
            "type": button.slug,
            "id": str(task_instance.id),
        },
    } for button in sorted_buttons]
    return buttons

