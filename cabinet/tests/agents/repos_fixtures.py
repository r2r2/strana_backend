from importlib import import_module
from secrets import token_urlsafe

from pytest import fixture


@fixture(scope="function")
def agent_repo():
    agent_repo = getattr(import_module("src.agents.repos"), "AgentRepo")()
    return agent_repo


@fixture(scope="function")
def agent_authorization(agent):
    token_creator = getattr(import_module("common.security"), "create_access_token")
    jwt = token_creator(agent.type.value, agent.id, {"agency_id": agent.agency_id})
    authorization = f"{jwt['type'].capitalize()} {jwt['token']}"
    return authorization


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


@fixture(scope="function")
async def agent(agent_repo, active_agency):
    data = {
        "name": "test",
        "type": "agent",
        "is_active": True,
        "surname": "string",
        "is_approved": True,
        "patronymic": "string",
        "email": "test_email@email.com",
        "email_token": token_urlsafe(32),
        "agency_id": active_agency.id,
        "maintained_id": active_agency.id,
    }
    agent = await agent_repo.update_or_create({"phone": "+79296010018"}, data)
    return agent
