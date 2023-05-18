from typing import Type, Any

from ..entities import BasePageCase
from ..repos import ShowtimeRegistrationRepo, ShowtimeRegistration


class ShowtimeRegistrationRetrieveCase(BasePageCase):
    """
    Страница записи на показ
    """

    def __init__(self, showtime_registration_repo: Type[ShowtimeRegistrationRepo]) -> None:
        self.showtime_registration_repo: ShowtimeRegistrationRepo = showtime_registration_repo()

    async def __call__(self) -> ShowtimeRegistration:
        filters: dict[str, Any] = dict()
        showtime_registration: ShowtimeRegistration = await self.showtime_registration_repo.retrieve(
            filters=filters
        )
        return showtime_registration
