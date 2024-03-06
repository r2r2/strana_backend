import structlog
from typing import Any

from src.booking.exceptions import BookingNotFoundError
from src.booking.repos import BookingEventHistoryRepo, BookingRepo, Booking
from src.users.repos import UserRepo, User


class BookingEventHistoriesCase:
    def __init__(
            self,
            booking_repo: BookingRepo,
            user_repo: UserRepo,
            booking_event_history_repo: BookingEventHistoryRepo,
            logger: Any = structlog.getLogger(__name__),
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo
        self.user_repo: UserRepo = user_repo
        self.booking_event_history_repo: BookingEventHistoryRepo = booking_event_history_repo
        self.logger = logger

    async def __call__(self, booking_id: int, user_id: int) -> dict:
        booking: Booking | None = await self.get_booking(booking_id, user_id)
        if not booking:
            self.logger.error(f"BookingEventHistoriesCase | Booking with {booking_id=} {user_id=} does not exist")
            raise BookingNotFoundError

        event_histories: list[dict[str, Any]] = (
            await self.booking_event_history_repo.list(
                filters={"booking_id": booking.id},
                ordering="-date_time"
            ).values(
                "id",
                "event_slug",
                "event_name",
                "event_description",
                "date_time",
                "group_status_until",
                "group_status_after",
                "task_name_until",
                "task_name_after",
                "event_status_until",
                "event_status_after",
            )
        )
        return {
            "count": len(event_histories) if event_histories else 0,
            "result": event_histories
        }

    async def get_booking(self, booking_id: int, user_id: int) -> Booking | None:
        user: User = await self.user_repo.retrieve(filters={"id": user_id})
        if not user:
            return

        booking: Booking = await self.booking_repo.retrieve(
            filters={"id": booking_id, "user_id": user.id}
        )
        return booking
