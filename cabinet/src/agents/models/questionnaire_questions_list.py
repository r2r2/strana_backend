from typing import Optional

from pydantic import validator, root_validator
from fastapi import Body

from src.questionnaire.constants import QuestionType
from src.questionnaire.repos import UserAnswer
from common.pydantic import CamelCaseBaseModel


class _AnswerResponse(CamelCaseBaseModel):
    id: Optional[int]
    title: Optional[str]
    description: Optional[str]
    hint: Optional[str]

    class Config:
        orm_mode = True


class QuestionsListResponse(CamelCaseBaseModel):
    id: int
    title: str
    description: str
    type: QuestionType
    initial_value: Optional[int]
    answer_default: Optional[int]
    required: bool
    options: list[_AnswerResponse]

    @validator("initial_value", "answer_default", pre=True)
    def _initial_value(cls, value: list):
        if value:
            return value.pop().answer_id if isinstance(value[0], UserAnswer) else None
        return None

    @root_validator
    def _answer_default(cls, values):
        if not values.get("initial_value"):
            values["initial_value"] = values.get("answer_default")
        del values["answer_default"]
        return values

    class Config:
        orm_mode = True


class FinishQuestionRequest(CamelCaseBaseModel):
    booking_id: int = Body(..., description="ID сделки")


class CurrentAnswerRequest(CamelCaseBaseModel):
    option: int
    booking_id: int


class RequiredQuestionResponse(CamelCaseBaseModel):
    id: int
    reason: str = "required_to_answer"


class FinishQuestionResultResponse(CamelCaseBaseModel):
    is_finished: bool
    errors: list[Optional[RequiredQuestionResponse]]
