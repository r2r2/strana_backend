from typing import Type
from ..entities import BaseUserCase
from ..exceptions import UserNotFoundError, CheckNotFoundError
from ..models import RequestAdminCommentModel
from ..repos import User, CheckRepo, Check
from ...agents.repos import AgentRepo
from ...admins.types import AdminEmail


class AdminsAgentsDisputeCommendCase(BaseUserCase):
    """
    Сохранение комментария админа
    """

    def __init__(
        self,
        agent_repo: Type[AgentRepo],
        check_repo: Type[CheckRepo],
    ) -> None:
        self.agent_repo: AgentRepo = agent_repo()
        self.check_repo: CheckRepo = check_repo()

    async def __call__(self, admin_id: int, payload: RequestAdminCommentModel) -> Check:
        data = payload.dict(exclude_unset=True)
        admin_comment = data.get("comment")
        filters = dict(id=payload.user_id)
        user: User = await self.agent_repo.retrieve(filters=filters)
        if not user:
            raise UserNotFoundError
        if not user.phone:
            raise ValueError("У проверяемого пользователя нет номера телефона")

        filters = dict(user_id=payload.user_id)
        check: Check = await self.check_repo.retrieve(filters=filters, ordering="-id")
        if not check:
            raise CheckNotFoundError

        if admin_comment:
            data = dict(admin_comment=admin_comment)
            await self.check_repo.update(check, data=data)
            await check.refresh_from_db(fields=['admin_comment'])

        return check
