from http import HTTPStatus

from src.questionnaire.entities import BaseQuestionnaireException


class QuestionnaireUploadDocumentNotFoundError(BaseQuestionnaireException):
    message: str = "Загруженные документы не найдены."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "questionnaire_upload_document_not_found"
