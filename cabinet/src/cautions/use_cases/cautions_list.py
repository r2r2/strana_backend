from typing import List

from src.cautions.entities import BaseCautionCase
from src.cautions.repos import Caution
from src.cautions.services.available_cautions import AvailableCautionsForUserService


class CautionListCase(BaseCautionCase):
    """ Получение всех предупреждений для пользователя
    """
    def __init__(
        self,
        caution_service: AvailableCautionsForUserService
    ):
        self.caution_service = caution_service

    async def __call__(self, user_id: int) -> List[Caution]:
        return await self.caution_service(user_id=user_id)
