from http import HTTPStatus
from typing import Type

import structlog
from common.paginations import PagePagination
from fastapi import HTTPException
from src.users.repos import User, UserRepo
from src.users.constants import UserType

from ..entities import BaseMeetingCase
from ..repos import Meeting, MeetingRepo


class MeetingsListCase(BaseMeetingCase):
    """
    Кейс для списка встреч.
    """
    def __init__(
        self,
        meeting_repo: Type[MeetingRepo],
        user_repo: Type[UserRepo],
    ) -> None:
        self.meeting_repo: MeetingRepo = meeting_repo()
        self.user_repo: UserRepo = user_repo()
        self.logger = structlog.getLogger(__name__)

    async def __call__(
        self,
        *,
        statuses: list[str],
        user_id: int,
        client_id: int,
        booking_id: int,
        pagination: PagePagination,
    ) -> dict:
        user: User = await self.user_repo.retrieve(filters=dict(id=user_id))

        filters: dict = {}
        if client_id and user.type in [UserType.AGENT, UserType.REPRES]:
            self.logger.info(f"Add filter with {client_id=}")
            filters.update(
                booking__user_id=client_id,
                booking__agent_id=user_id,
            )
        elif booking_id and user.type in [UserType.AGENT, UserType.REPRES]:
            self.logger.info(f"Add filter with {booking_id=}")
            filters.update(
                booking_id=booking_id,
                booking__agent_id=user.id,
            )
        elif user.type == UserType.CLIENT:
            filters.update(booking__user_id=user_id)
        else:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if statuses:
            self.logger.info(f"Add filter with {statuses=}")
            filters.update(status__slug__in=statuses)

        meetings: list[Meeting] = await self.meeting_repo.list(
            filters=filters,
            start=pagination.start,
            end=pagination.end,
            related_fields=["booking", "status", "booking__agent", "booking__agency"],
            ordering="-date",
        )

        counted = await self.meeting_repo.list(
            filters=filters,
        ).count()

        data: dict = dict(
            count=counted,
            result=meetings,
            page_info=pagination(count=counted)
        )
        return data
