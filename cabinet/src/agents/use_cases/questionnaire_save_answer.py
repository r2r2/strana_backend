from src.questionnaire.repos import QuestionRepo, Question, UserAnswerRepo
from src.booking.repos import BookingRepo, Booking
from src.booking.exceptions import BookingNotFoundError
from ..entities import BaseAgentCase
from ..exceptions import QuestionNotFoundError
from ..models import CurrentAnswerRequest


class QuestionareSaveAnswerCase(BaseAgentCase):
    """
    Кейс сохранения ответа пользователя
    """
    def __init__(
            self,
            booking_repo: type[BookingRepo],
            question_repo: type[QuestionRepo],
            users_answer_repo: type[UserAnswerRepo],
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.question_repo: QuestionRepo = question_repo()
        self.users_answer_repo: UserAnswerRepo = users_answer_repo()

    async def __call__(self, *, question_id: int, payload: CurrentAnswerRequest) -> None:
            booking: Booking = await self.booking_repo.retrieve(filters=dict(id=payload.booking_id))
            if not booking:
                raise BookingNotFoundError

            question: Question = await self.question_repo.retrieve(
                filters=dict(id=question_id),
                prefetch_fields=["question_group"]
            )
            if not question:
                raise QuestionNotFoundError

            user_answer_filters: dict = dict(
                question_id=question_id,
                question_group_id=question.question_group.id,
                user_id=booking.user_id,
                booking_id=payload.booking_id
            )
            await self.users_answer_repo.get_or_create_and_update(
                filters=user_answer_filters, data=dict(answer_id=payload.option)
            )
