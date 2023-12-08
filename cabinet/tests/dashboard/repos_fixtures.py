from importlib import import_module
from pytest import fixture

from src.dashboard.repos import TicketRepo, Ticket, Slider, SliderRepo


@fixture(scope="function")
def ticket_repo() -> TicketRepo:
    ticket_repo: TicketRepo = getattr(
        import_module("src.dashboard.repos"), "TicketRepo"
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


@fixture(scope="function")
def slide_repo() -> SliderRepo:
    slide_repo: SliderRepo = getattr(
        import_module("src.dashboard.repos"), "SliderRepo"
    )()
    return slide_repo


@fixture(scope="function")
async def slide(slide_repo, faker) -> Slider:
    data = {
    "is_active": True,
    "sort": faker.random_int(min=10000000, max=99999999),
    "title": faker.text(),
    "subtitle": faker.text(),
    }
    slide: Slider = await slide_repo.create(data=data)
    return slide
