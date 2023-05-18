from tortoise.queryset import QuerySet

from src.questionnaire.repos import QuestionRepo, Question
from src.booking.repos import BookingRepo, Booking
from src.booking.exceptions import BookingNotFoundError
from ..entities import BaseAgentCase
from ..models import FinishQuestionRequest


class QuestionareFinishCase(BaseAgentCase):
    """
    Кейс конца опросника
    """
    def __init__(
            self,
            booking_repo: type[BookingRepo],
            question_repo: type[QuestionRepo],
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.question_repo: QuestionRepo = question_repo()

    async def __call__(self, *, slug: str, payload: FinishQuestionRequest) -> dict:
        booking_id: int = payload.booking_id
        is_finished: bool = True

        booking: Booking = await self.booking_repo.retrieve(filters=dict(id=booking_id))
        if not booking:
            raise BookingNotFoundError

        question_filters: dict = dict(question_group__func_block__slug=slug, is_active=True, required=True)
        standards_question_qs: QuerySet = self.question_repo.list(filters=question_filters, ordering="sort")
        question_filters.update(dict(user_question__booking_id=booking_id))
        answered_questions_qs: QuerySet = self.question_repo.list(filters=question_filters)

        standards_questions: list[Question] = await standards_question_qs
        answered_questions: list[Question] = await answered_questions_qs
        unanswered_questions: list[Question] = list(set(standards_questions).difference(set(answered_questions)))

        if unanswered_questions:
            is_finished: bool = False

        data: dict = dict(is_finished=is_finished, errors=unanswered_questions)
        return data
