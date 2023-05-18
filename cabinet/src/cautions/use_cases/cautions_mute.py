from typing import Type

from src.cautions.entities import BaseCautionCase
from src.cautions.exceptions import CautionNotFoundError
from src.cautions.repos import CautionMuteRepo, CautionRepo, Caution
from src.users.exceptions import UserNotFoundError
from src.users.repos import UserRepo, User


class CautionMuteCase(BaseCautionCase):
    """Заглушение предупреждения для конкретного пользователя"""
    def __init__(
        self,
        caution_repo: Type[CautionRepo],
        caution_mute_repo: Type[CautionMuteRepo],
        user_repo: Type[UserRepo]
    ):
        self.caution_mute_repo = caution_mute_repo()
        self.caution_repo = caution_repo()
        self.user_repo = user_repo()

    async def __call__(self, user_id: int, caution_id: int) -> None:
        user: User = await self.user_repo.retrieve(filters=dict(id=user_id))
        if not user:
            raise UserNotFoundError

        caution: Caution = await self.caution_repo.retrieve(filters=dict(id=caution_id))
        if not caution:
            raise CautionNotFoundError

        filters = dict(
            user__id=user_id,
            caution__id=caution_id
        )
        data = dict(
            user_id=user_id,
            caution_id=caution_id
        )

        await self.caution_mute_repo.update_or_create(filters=filters, data=data)
