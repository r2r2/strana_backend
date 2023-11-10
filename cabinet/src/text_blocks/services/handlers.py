from http import HTTPStatus
from typing import Any, Type, Optional

from fastapi import HTTPException
from src.booking import repos as booking_repos
from ..entities import BaseTextBlockCase
from ..repos.text_block import TextBlock
from src.users import repos as users_repos
from src.users.constants import UserType
from ..exceptions import AgentDataIncorrectError


class TextBlockHandlerService(BaseTextBlockCase):
    """
    Кейс для получения текстовых блоков при увольнении агента.
    """

    handlers = {
        "repres_fire_agent_modal": "fire_agent_handler",
        "repres_fire_agent_success": "fire_agent_handler",
        "admin_fire_agent_modal": "fire_agent_handler",
        "admin_fire_agent_success": "fire_agent_handler",
        "agent_fire_modal": "fire_agent_handler",
    }

    def __init__(
        self,
        booking_repo: Type[booking_repos.BookingRepo],
        users_repo: Type[users_repos.UserRepo],
    ) -> None:
        self.booking_repo: booking_repos.BookingRepo = booking_repo()
        self.users_repo: users_repos.UserRepo = users_repo()

    async def __call__(self, slug: str, **kwargs) -> Any:
        handler = self.handlers.get(slug)
        if not handler:
            return
        else:
            return await getattr(self, handler)(**kwargs)

    async def fire_agent_handler(
        self,
        text_block: TextBlock,
        agent_id: Optional[int] = None,
        user_id: Optional[int] = None,
        **kwargs,
    ) -> Any:
        user = await self.users_repo.retrieve(filters=dict(id=user_id))
        user_type = user.type.value if user else None
        if not user or not user_type or (user_type not in (UserType.ADMIN, UserType.REPRES, UserType.AGENT)):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user_type == UserType.AGENT:
            agent = user
        else:
            agent = await self.users_repo.retrieve(filters=dict(id=agent_id, type=UserType.AGENT))
            if not agent or (user_type == UserType.REPRES and agent.agency_id and agent.agency_id != user.agency_id):
                raise AgentDataIncorrectError

        clients = await self.users_repo.count(filters=dict(agent_id=agent.id))
        active_bookings = await self.booking_repo.count(filters=dict(agent_id=agent.id, active=True))
        closed_bookings = await self.booking_repo.count(filters=dict(agent_id=agent.id, active=False))

        text_block.text = text_block.text.format(
            clients=clients,
            active_bookings=active_bookings,
            closed_bookings=closed_bookings,
        )

        return text_block
