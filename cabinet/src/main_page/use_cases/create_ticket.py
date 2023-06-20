from typing import Any

from src.cities.repos import CityRepo, City
from src.main_page.entities import BaseMainPageCase
from src.main_page.repos import TicketRepo, Ticket
from src.users.models import RequestCreateTicket


class CreateTicketCase(BaseMainPageCase):
    """
    Сценарий создания заявки
    """

    def __init__(
        self,
        ticket_repo: type[TicketRepo],
        city_repo: type[CityRepo],
    ):
        self.ticket_repo = ticket_repo()
        self.city_repo = city_repo()

    async def __call__(self, payload: RequestCreateTicket) -> None:
        city: City = await self.city_repo.retrieve(
            filters=dict(slug=payload.city),
        )

        data: dict[str, Any] = dict(
            name=payload.name,
            phone=payload.phone,
            type=payload.type,
        )
        ticket: Ticket = await self.ticket_repo.create(data=data)
        await ticket.city.add(city)
