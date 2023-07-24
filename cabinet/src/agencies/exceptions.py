from http import HTTPStatus

from .entities import BaseAgencyException


class AgencyNotFoundError(BaseAgencyException):
    message: str = "Агентство с таким ИНН не зарегистрировано в системе. Попробуйте зарегистрироваться как агентство."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "agency_not_found"


class AgencyNotApprovedError(BaseAgencyException):
    message: str = "Агентство не одобрено."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "agency_not_approved"


class AgencyDataTakenError(BaseAgencyException):
    message: str = "Введенные данные заняты."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "agency_data_taken"


class AgencyInvalidFillDataError(BaseAgencyException):
    message: str = "Неверные введенные данные."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "agency_invalid_fill_data"


class AgencyIncorrectPhoneForamtError(BaseAgencyException):
    message: str = "Некорректный номер телефона"
    status: int = HTTPStatus.UNPROCESSABLE_ENTITY
    reason: str = "agency_incorrect_phone_format"


class AgencyProjectNotFoundError(BaseAgencyException):
    message: str = "Проект не найден"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "agency_project_not_found"


class RepresAgencyNotFoundError(BaseAgencyException):
    message: str = "Агентство представителя не найдено"
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "agency_not_found"


class AgentAgencyNotFoundError(BaseAgencyException):
    message: str = "Агентство агента не найдено"
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "agency_not_found"


class AgencyAgreementAlreadyExists(BaseAgencyException):
    message: str = "Договор для данного ЖК уже существует"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "agreement_already_exists"


class AgencyDocTemplateNotExists(BaseAgencyException):
    message: str = "Шаблон документа не существует"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "template_not_exists"


class AgencyAgreementTypeNotExists(BaseAgencyException):
    message: str = "Типа документа не существует"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "agreement_type_not_exists"


class AgencyBookingNotExists(BaseAgencyException):
    message: str = "Бронирования не существует"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "booking_not_exists"


class AgencyActNotExists(BaseAgencyException):
    message: str = "Акт агентства не существует"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "agency_act_not_exists"


class AgencyAgreementNotExists(BaseAgencyException):
    message: str = "Договор агентства не существует"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "agency_agreement_not_exists"


class AdditionalAgreementNotExists(BaseAgencyException):
    message: str = "Дополнительного соглашения не существует"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "additional_agreement_not_exists"


class AdditionalAgreementAlreadyUpload(BaseAgencyException):
    message: str = "Документ для дополнительного соглашения уже загружен"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "additional_agreement_document_already_download"


class AgencyMainteinerNotExists(BaseAgencyException):
    message: str = "У агентства нет представителя"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "agency_maintainer_not_exists"


class InvalidAdminDataError(BaseAgencyException):
    status: int = HTTPStatus.BAD_REQUEST
