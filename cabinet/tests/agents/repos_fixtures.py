from importlib import import_module
from secrets import token_urlsafe

from pytest import fixture


@fixture(scope="function")
def agent_repo():
    agent_repo = getattr(import_module("src.agents.repos"), "AgentRepo")()
    return agent_repo


@fixture(scope="function")
def agent_factory(agent_repo, faker):
    async def agent(agency_id=None, i=0, email=None):
        data = {
            "email": email if email else faker.email(),
            "name": faker.name(),
            "surname": faker.name(),
            "patronymic": faker.name(),
            "birth_date": faker.date(),
            "passport_number": "123465",
            "passport_series": "9816",
            "type": "agent",
            "agency_id": agency_id,
            "phone": (
                faker.phone_number()
                .replace(" ", "")
                .replace("-", "")
                .replace("(", "")
                .replace(")", "")
            ),
        }
        return await agent_repo.create(data)

    return agent
