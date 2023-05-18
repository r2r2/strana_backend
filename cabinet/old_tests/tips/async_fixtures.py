from pytest import fixture


@fixture(scope="function")
async def tip(tip_repo):
    data = {"image": "test", "title": "test", "text": "test", "order": 1}
    tip = await tip_repo.update_or_create(data=data, filters={})
    return tip
