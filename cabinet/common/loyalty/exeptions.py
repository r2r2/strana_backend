from http import HTTPStatus


class BaseLoyaltyException(Exception):
    message: str = "Ошибка интеграции с МС лояльности"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "loyalty_error"
