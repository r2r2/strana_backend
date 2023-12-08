from enum import StrEnum


class QuestionType(StrEnum):
    """
    Тип вопроса
    """
    SINGLE: str = "single"
    MULTIPLE: str = "multiple"
