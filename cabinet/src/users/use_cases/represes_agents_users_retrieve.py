from typing import Any, Type, Union

from ..constants import UserType
from ..entities import BaseUserCase
from ..exceptions import UserNotFoundError
from ..repos import CheckRepo, User, UserRepo
from ..types import (UserBooking, UserBookingRepo, UserProperty,
                     UserPropertyRepo)


class RepresesAgentsUsersRetrieveCase(BaseUserCase):
    """
    Пользователь агента представителя агенства
    """

    def __init__(
        self,
        user_repo: Type[UserRepo],
        check_repo: Type[CheckRepo],
        booking_repo: Type[UserBookingRepo],
        property_repo: Type[UserPropertyRepo],
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.check_repo: CheckRepo = check_repo()
        self.booking_repo: UserBookingRepo = booking_repo()
        self.property_repo: UserPropertyRepo = property_repo()

    async def __call__(self, user_id: int, agency_id: int, agent_id: int) -> User:
        filters: dict[str, Any] = dict(agent_id=agent_id)
        check_qs: Any = self.check_repo.list(filters=filters, related_fields=["unique_status"])
        filters: dict[str, Any] = dict(
            id=user_id, agency_id=agency_id, checkers=agent_id, type=UserType.CLIENT
        )
        user: User = await self.user_repo.retrieve(
            filters=filters,
            related_fields=["agent", "agency"],
            prefetch_fields=[dict(relation="users_checks", queryset=check_qs, to_attr="checks")],
        )
        if not user:
            raise UserNotFoundError
        if user.agent_id and int(user.agent_id) == int(agent_id):
            filters: dict[str, Any] = dict(interested_users=user_id)
            properties: list[UserProperty] = await self.property_repo.list(
                filters=filters, related_fields=["floor", "project", "building"]
            )
            filters: dict[str, Any] = dict(
                user_id=user_id, active=True, agency_id=agency_id, agent_id=agent_id
            )
            bookings: list[UserBooking] = await self.booking_repo.list(
                filters=filters, related_fields=["floor", "project", "building", "property"]
            )
            user: Union[dict, list] = self.user_repo.c_builder.denormalize(
                bases=user,
                update=True,
                to="interesting",
                objects=properties,
                pattern=dict(property="", floor="floor", project="project", building="building"),
            )
            user: Union[dict, list] = self.user_repo.c_builder.denormalize(
                bases=user, update=True, to="indents", objects=bookings
            )
        return user
