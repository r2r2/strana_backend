from enum import Enum


class QuestionType(str, Enum):
    """
    Тип вопроса
    """
    SINGLE: str = "single"
    MULTIPLE: str = "multiple"
