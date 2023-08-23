from http import HTTPStatus

from .entities import BaseCheckException, BaseUserException


class UserCodeTimeoutError(BaseUserException):
    message: str = "Время кода истекло."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "user_code_timeout"


class UserNotFoundError(BaseUserException):
    message: str = "Пользователь не найден."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "user_not_found"


class UserWasDeletedError(BaseUserException):
    message: str = "Ползователь был удален"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "user_was_deleted"


class UserWrongCodeError(BaseUserException):
    message: str = "Неверный код."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "wrong_code"


class UserWrongPasswordError(BaseUserException):
    message: str = "Введен неверный пароль."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "password_wrong"


class UserNotApprovedError(BaseUserException):
    message: str = "Пользователь не одобрен."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "user_not_approved"


class UserMaxCodeAttemptsError(BaseUserException):
    message: str = (
        "Превышено максимальное количество попыток ввода кода, попробуйте через 10 минут."
    )
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "max_code_attempts"


class UserAlreadyRegisteredError(BaseUserException):
    message: str = "Пользователь уже зарегистрирован."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "user_already_registered"


class UserSendSmsError(BaseUserException):
    message: str = "Ошибка отправки смс."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "user_send_sms"


class UserEmailTakenError(BaseUserException):
    message: str = "Введенный email занят."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "user_email_taken"


class UserPhoneTakenError(BaseUserException):
    message: str = "Введенный телефон занят."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "user_phone_taken"


class UserSamePhoneError(BaseUserException):
    message: str = "Введен прежний телефон."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "user_phone_same"


class UserWrongTypeError(BaseUserException):
    message: str = "Пользователь имеет другую роль."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "user_wrong_type"


class UserChangePhoneError(BaseUserException):
    message: str = "Ошибка смены телефона."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "user_change_phone"


class UserNoProjectError(BaseUserException):
    message: str = "Выбран неверный проект."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "user_no_project"


class UserCheckLaterError(BaseUserException):
    message: str = "Проверьте клиента позже."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "user_check_later"


class UserMissMatchError(BaseUserException):
    message: str = "Данные не совпадают."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "user_miss_match"


class UserAlreadyBoundError(BaseUserException):
    message: str = "Пользователь уже привязан."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "user_already_bound"


class UserAmoCreateError(BaseUserException):
    message: str = "Пользователь не был создан в амо."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "user_amo_create"


class UserAgentMismatchError(BaseUserException):
    message: str = "Агент не привязан к клиенту"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "user_agent_mismatch"


class UserNoAgentError(BaseUserException):
    message: str = "Агент пользователя не найден."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "user_no_agent"


class UserNoAgencyError(BaseUserException):
    message: str = "Агентство пользователя не найдено."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "user_no_agency"


class CheckNotFoundError(BaseCheckException):
    message: str = "Запрашиваемая проверка не найдена."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "check_not_found"


class CheckNotUniqueError(BaseCheckException):
    message: str = "Клиент неуникален, вы не можете его передать."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "check_not_unique"


class UserNotUnique(BaseUserException):
    message: str = "Пользователь не уникальный"
    status: int = HTTPStatus.FORBIDDEN
    reason: str = "User is not unique"


class UserChangePasswordError(BaseUserException):
    message: str = "Ошибка смены пароля."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "user_change_password"


class UserSamePasswordError(BaseUserException):
    message: str = "Пароль остался неизменным."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "user_same_password"


class UserPasswordTimeoutError(BaseUserException):
    message: str = "Время смены истекло."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "user_password_timeout"


class UserIncorrectPhoneForamtError(BaseUserException):
    message: str = "Некорректный номер телефона"
    status: int = HTTPStatus.UNPROCESSABLE_ENTITY
    reason: str = "user_incorrect_phone_format"


class UserAgentHasNoAgency(BaseUserException):
    message: str = "Отсутствует агентство у агента."
    status: int = HTTPStatus.FORBIDDEN
    reason: str = "user_has_no agency"


class NotUniquePhoneUser(BaseUserException):
    message: str = "Простите, данный номер телефона закреплен за другим {}, вы не можете его использовать."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "phone_is_already_used"


class NotUniqueEmailUser(BaseUserException):
    message: str = "Простите, данная почта закреплена за другим {}, вы не можете её использовать."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "email_is_already_used"


class NotUniqueEmaiAndPhoneUser(BaseUserException):
    message: str = "Простите, данная почта закреплена за другим {mail_match_user_type}, телефон закреплен за другим " \
                   "{phone_match_user_type}, вы не можете их использовать."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "email_and_phone_is_already_used"


class UserIncorrectPhoneFormat(BaseUserException):
    message: str = "Некорректный номер телефона"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "user_incorrect_phone_format"


class UserIncorrectEmailFormat(BaseUserException):
    message: str = "Некорректный почтовый ящик"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "user_incorrect_email_format"


class ConfirmClientAssignNotFoundError(BaseUserException):
    message: str = "Запрашиваемая проверка не найдена."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "confirm_client_assign_not_found"


class UniqueStatusNotFoundError(BaseUserException):
    message: str = "Статус не найден."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "unique_status_not_found"


class WrongSuperuserAuthAsUserDataError(BaseUserException):
    message: str = "Неверные данные для авторизации суперюзера под пользователем"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "wrong_superuser_auth_user_data"
