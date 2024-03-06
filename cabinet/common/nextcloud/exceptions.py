from http import HTTPStatus


class NextcloudAPIError(Exception):
    message: str = "Ошибка интеграции с Nextcloud"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "nextcloud_error"
