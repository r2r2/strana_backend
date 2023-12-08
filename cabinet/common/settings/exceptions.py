from http import HTTPStatus

from common.settings.entities import BaseSettingsException


class SystemListNotFoundError(BaseSettingsException):
    """
    Система не найдена
    """
    message = "Система не найдена"
    status = HTTPStatus.NOT_FOUND
    reason = "system_not_found"
