from http import HTTPStatus
from .entities import BaseAgentException


class AgentWrongPasswordError(BaseAgentException):
    message: str = "Введен неверный пароль."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "agent_password_wrong"


class AgentNotApprovedError(BaseAgentException):
    message: str = "Агент не одобрен."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "agent_not_approved"


class AgentAlreadyRegisteredError(BaseAgentException):
    message: str = "Агент уже зарегистрирован."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "agent_already_registered"


class AgentNotFoundError(BaseAgentException):
    message: str = "Агент не найден."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "agent_not_found"


class AgentWasDeletedError(BaseAgentException):
    message: str = "Агент был удален"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "agent_was_deleted"


class AgentChangePasswordError(BaseAgentException):
    message: str = "Ошибка смены пароля."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "agent_change_password"


class AgentConfirmEmailError(BaseAgentException):
    message: str = "Не подтверждена почта."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "agent_email_confirm"


class AgentSamePasswordError(BaseAgentException):
    message: str = "Пароль остался неизменным."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "agent_same_password"


class AgentPasswordTimeoutError(BaseAgentException):
    message: str = "Время смены истекло."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "agent_password_timeout"


class AgentEmailTakenError(BaseAgentException):
    message: str = "Введенный email занят."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "agent_email_taken"


class AgentNoAgencyError(BaseAgentException):
    message: str = "Агентство не одобрено."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "agent_no_agency"


class AgentDataTakenError(BaseAgentException):
    message: str = "Введенные данные заняты."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "agent_data_taken"


class AgentPhoneTakenError(BaseAgentException):
    message: str = "Введенный телефон занят."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "agent_phone_taken"


class AgentPasswordsDoesntMatch(BaseAgentException):
    message: str = "Пароли не совпадают."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "agent_passwords_doesnt_match"


class AgentIncorrectPhoneForamtError(BaseAgentException):
    message: str = "Некорректный номер телефона"
    status: int = HTTPStatus.UNPROCESSABLE_ENTITY
    reason: str = "agent_incorrect_phone_format"


class QuestionNotFoundError(BaseAgentException):
    message: str = "Вопрос не найден."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "question_not_found"


class QuestionsNotFoundError(BaseAgentException):
    message: str = "Вопросы не найдены."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "questions_not_found"


class DocumentsBlocksNotFoundError(BaseAgentException):
    message: str = "Блоки документов не найдены."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "documents_blocks_not_found"


class FunctionalBlockNotFoundError(BaseAgentException):
    message: str = "Функциональный блок документов не найдены."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "functional_block_not_found"


class DocumentNotFoundError(BaseAgentException):
    message: str = "Документ не найден."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "document_not_found"


class UploadDocumentsNotFoundError(BaseAgentException):
    message: str = "Загруженные документы не найдены."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "upload_documents_not_found"


class UploadDocumentInternalError(BaseAgentException):
    message: str = "Ошибка сервиса загрузки файлов"
    status: int = HTTPStatus.INTERNAL_SERVER_ERROR
    reason: str = "upload_service_internal_error"


class AgentHasNoAgencyError(BaseAgentException):
    message: str = "У агента нет агентства."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "agent_has_no_agency_error"


class AgentHasAgencyError(BaseAgentException):
    message: str = "У агента уже есть агентство"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "agent_has_agency_error"
