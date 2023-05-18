from secrets import token_urlsafe

from pytest import fixture


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
    }
    agent = await agent_repo.update_or_create({"phone": "+79296010018"}, data)
    return agent
