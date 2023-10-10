import structlog
from typing import Optional

from common.amocrm.types import AmoContact
from ..services.create_contact import CreateContactService
from ..exceptions import UserNotFoundError
from ..repos import User
from ..loggers.wrappers import user_changes_logger


class UpdateUsersService(CreateContactService):
    """
    Импорт(обновление) данных пользователей из AmoCRM
    """

    logger = structlog.getLogger(__name__)

    async def __call__(self, user_id: int):
        user: User = await self.user_repo.retrieve(filters=dict(id=user_id))
        if not user:
            raise UserNotFoundError

        async with await self.amocrm_class() as amocrm:
            contact: Optional[AmoContact] = await amocrm.fetch_contact(user_id=user.amocrm_id)
            if not contact:
                self.logger.warning("User has not found at amo contact")
                return

            data = await self.fetch_amocrm_data(contact)
            await user_changes_logger(
                self.user_repo.update, self, content="Импорт данных пользователей из AmoCRM"
            )(user=user, data=data)
