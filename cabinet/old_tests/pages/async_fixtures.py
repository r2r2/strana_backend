from pytest import fixture


@fixture(scope="function")
async def broker_registration(broker_registration_repo):
    broker_registration = await broker_registration_repo.create(data=dict())
    return broker_registration
