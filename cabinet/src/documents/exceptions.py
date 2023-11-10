from http import HTTPStatus

from .entities import BaseDocumentException


class DocumentNotFoundError(BaseDocumentException):
    message: str = "Документ не найден."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "document_not_found"


class EscrowNotFoundError(BaseDocumentException):
    message: str = "Памятка эскроу не найдена."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "escrow_document_not_found"


class InstructionNotFoundError(BaseDocumentException):
    message: str = "Инструкция не найдена."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "instruction_not_found"


class InteractionDocumentNotFoundError(BaseDocumentException):
    message: str = "Взаимодействия не найдены."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "interaction_not_found"