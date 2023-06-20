from importlib import import_module
from pytest import fixture

from src.main_page.repos import TicketRepo, Ticket


@fixture(scope="function")
def ticket_repo() -> TicketRepo:
    ticket_repo: TicketRepo = getattr(
        import_module("src.main_page.repos"), "TicketRepo"
    )()
    return ticket_repo


@fixture(scope="function")
async def ticket(ticket_repo, faker, city) -> Ticket:
    data = {
        "name": faker.name(),
        "phone": faker.phone_number(),
        "user_amocrm_id": faker.random_int(min=10000000, max=99999999),
        "booking_amocrm_id": faker.random_int(min=10000000, max=99999999),
        "note": faker.text(),
        "type": faker.word(),
        "city_id": city.id,
    }
    ticket: Ticket = await ticket_repo.create(data=data)
    return ticket
