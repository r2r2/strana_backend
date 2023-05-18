import json

from common.loggers.utils import get_difference_between_two_dicts
from ..repos import User, UserRepo
from ..entities import BaseUserCase


def user_changes_logger(user_change: UserRepo(), use_case: BaseUserCase, content: str):
    from src.users.tasks import create_user_log_task
    """
    Логирование изменений пользователя
    """

    async def _wrapper(user: User = None, data: dict = None, filters: dict = None):
        user_after, response_data = dict(), dict()
        user_before = json.dumps(dict(user), indent=4, sort_keys=True, default=str) if user else dict()
        user_difference = dict()
        error_data = None

        if data and filters:
            update_user = user_change(filters=filters, data=data)
        elif user and isinstance(data, dict):
            update_user = user_change(model=user, data=data)
        elif user:
            update_user = user_change(model=user)
        else:
            update_user = user_change(data=data)

        try:
            user: User = await update_user
            user_id = user.id if user else None
            user_after = json.dumps(dict(user), indent=4, sort_keys=True, default=str) if user else dict()
            user_difference = get_difference_between_two_dicts(user_before, user_after)
        except Exception as error:
            error_data = str(error)
            user_id = None

        log_data: dict = dict(
            state_before=user_before,
            state_after=user_after,
            state_difference=user_difference,
            content=content,
            user_id=user_id,
            response_data=response_data,
            use_case=use_case.__class__.__name__,
            error_data=error_data,
        )

        await create_user_log_task(log_data=log_data)

        return user

    return _wrapper
