from ..services import UserCheckUniqueService
from ..entities import BaseUserCase
from ..models import RequestUserCheckUnique


class UserCheckUniqueCase(BaseUserCase):
    """
    Проверка уникальности пользователя в базе по телефону и почте.
    """

    def __init__(
        self,
        check_user_unique_service: UserCheckUniqueService
    ) -> None:
        self.check_user_unique_service: UserCheckUniqueService = check_user_unique_service

    async def __call__(
        self,
        payload: RequestUserCheckUnique,
    ) -> dict[str, bool]:

        await self.check_user_unique_service(payload)

        return dict(is_unique=True)

