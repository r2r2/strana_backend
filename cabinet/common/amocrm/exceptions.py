from fastapi import status


class BaseAmocrmException(Exception):
    """
    Базовый класс для исключений АмоЦРМ
    """

    message: str
    status: int
    reason: str


class AmocrmHookError(BaseAmocrmException):
    def __init__(
        self,
        message: str = "Ошибка интеграции с AMO CRM. Пожалуйста, повторите попытку позже.",
        reason: str = "amocrm_hook_exception",
    ):
        self.message = message
        self.reason = reason

    status: int = status.HTTP_502_BAD_GATEWAY


class AmoNoContactError(BaseAmocrmException):
    message: str = "Пользователь не существует в амо"
    status: int = status.HTTP_404_NOT_FOUND
    reason: str = "not_found_amo_contact"


class AmoContactIncorrectPhoneFormatError(BaseAmocrmException):
    message: str = "Некорректный номер телефона в АМО-ЦРМ"
    status: int = status.HTTP_422_UNPROCESSABLE_ENTITY
    reason: str = "incorrect_amo_contact_phone_format"


class AmoForbiddenError(BaseAmocrmException):
    message: str = "Ошибка доступа АМО-ЦРМ"
    status: int = status.HTTP_403_FORBIDDEN
    reason: str = "forbidden_amo_error"


class AmoTryAgainLaterError(BaseAmocrmException):
    message: str = "Произошла ошибка. Попробуйте через несколько минут"
    status: int = status.HTTP_400_BAD_REQUEST
    reason: str = "try_again_later"


class AmoFetchLeadNotFoundError(BaseAmocrmException):
    message: str = "Лид не найден"
    status: int = status.HTTP_404_NOT_FOUND
    reason: str = "amo_fetch_lead_not_found_error"


class AmoNoMainContactError(BaseAmocrmException):
    message: str = "No main contact in lead"
    status: int = status.HTTP_404_NOT_FOUND
    reason: str = "no_main_contact_error"
