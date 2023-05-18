from pytest import fixture
from importlib import import_module


@fixture(scope="function")
def notification_repo():
    notification_repo = getattr(import_module("src.notifications.repos"), "NotificationRepo")()
    return notification_repo


@fixture(scope="function")
def notification_factory(notification_repo, faker):
    async def notification(user_id=None):
        data = {"message": faker.name(), "user_id": user_id}
        return await notification_repo.create(data)

    return notification
