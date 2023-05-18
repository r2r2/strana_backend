from typing import Any, TypedDict

from ..constants import AmoEntityTypes, AmoTaskTypes


class AmoTask(TypedDict):
    id: int
    created_by: int
    updated_by: int
    created_at: int
    updated_at: int
    responsible_user_id: int
    group_id: int
    entity_id: int
    entity_type: AmoEntityTypes
    duration: int
    is_completed: bool
    task_type_id: AmoTaskTypes
    text: str
    result: Any
    complete_till: int
    account_id: int
    _links: Any
