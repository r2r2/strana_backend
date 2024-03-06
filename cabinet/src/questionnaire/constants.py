from enum import StrEnum


class QuestionType(StrEnum):
    """
    Тип вопроса
    """
    SINGLE: str = "single"
    MULTIPLE: str = "multiple"


class UploadedFileName(StrEnum):
    """
    Имя файла
    """
    PASSPORT: str = "mortgage_passport"
    SNILS: str = "mortgage_snils"
    MARRIAGE_CERTIFICATE: str = "mortgage_marriage_certificate"
    CHILD_BIRTH_CERTIFICATE: str = "mortgage_child_birth_certificate"
    NDFL_2: str = "mortgage_ndfl_2"
    LABOR_BOOK: str = "mortgage_labor_book"
    CERTIFICATES: str = "mortgage_certificates"
    CO_BORROWERS: str = "mortgage_co_borrowers"
    INN: str = "mortgage_inn"
