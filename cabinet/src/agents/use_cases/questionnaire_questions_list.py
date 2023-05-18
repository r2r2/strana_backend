from tortoise.queryset import QuerySet

from src.questionnaire.repos import AnswerRepo, QuestionRepo, Question, UserAnswerRepo
from src.booking.repos import BookingRepo, Booking
from src.booking.exceptions import BookingNotFoundError
from ..entities import BaseAgentCase
from ..exceptions import QuestionsNotFoundError


class QuestionsListResponseCase(BaseAgentCase):
    """
    Кейс получение вопросов опросника
    """
    def __init__(
            self,
            answer_repo: type[AnswerRepo],
            booking_repo: type[BookingRepo],
            question_repo: type[QuestionRepo],
            users_answer_repo: type[UserAnswerRepo],
    ) -> None:
        self.answer_repo: AnswerRepo = answer_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.question_repo: QuestionRepo = question_repo()
        self.users_answer_repo: UserAnswerRepo = users_answer_repo()

    async def __call__(self, slug: str, booking_id: int):
        booking_filters: dict = dict(id=booking_id)

        booking: Booking = await self.booking_repo.retrieve(filters=booking_filters)
        if not booking:
            raise BookingNotFoundError

        user_answer_qs: QuerySet = self.users_answer_repo.list(filters=dict(booking_id=booking_id))
        answers_qs: QuerySet = self.answer_repo.list(filters=dict(is_active=True), ordering='sort')
        answers_default_qs: QuerySet = self.answer_repo.list(filters=dict(is_active=True, is_default=True))
        questions_filters: dict = dict(question_group__func_block__slug=slug, is_active=True)
        questions_prefetch: list = [
            dict(relation="answers", queryset=answers_qs, to_attr="options"),
            dict(relation="user_question", queryset=user_answer_qs, to_attr="initial_value"),
            dict(relation="answers", queryset=answers_default_qs, to_attr="answer_default"),
        ]

        questions_qs: QuerySet = self.question_repo.list(
            filters=questions_filters,
            prefetch_fields=questions_prefetch,
        ).order_by("sort")

        questions: list[Question] = await questions_qs
        if not questions:
            raise QuestionsNotFoundError

        return questions
