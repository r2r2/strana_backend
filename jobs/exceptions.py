class AppException(Exception):
    ...  # noqa CCE002


class TaskLogicException(AppException):
    """Ошибка в логике работы задачи"""
