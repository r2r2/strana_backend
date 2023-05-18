from pytest import fixture
from secrets import token_urlsafe


@fixture(scope="function")
async def admin(admin_repo):
    data = {
        "name": "test",
        "type": "admin",
        "is_active": True,
        "surname": "string",
        "is_approved": True,
        "patronymic": "string",
        "email": "test_email_admin@email.com",
        "email_token": token_urlsafe(32),
    }
    admin = await admin_repo.update_or_create({"phone": "+79296010020"}, data)
    return admin
