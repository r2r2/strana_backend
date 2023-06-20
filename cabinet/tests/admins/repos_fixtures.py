from importlib import import_module
from secrets import token_urlsafe

from pytest import fixture


@fixture(scope="function")
def admin_repo():
    admin_repo = getattr(import_module("src.admins.repos"), "AdminRepo")()
    return admin_repo


@fixture(scope="function")
def admin_authorization(admin):
    token_creator = getattr(import_module("common.security"), "create_access_token")
    jwt = token_creator(admin.type.value, admin.id, {})
    authorization = f"{jwt['type'].capitalize()} {jwt['token']}"
    return authorization


@fixture(scope="function")
def admin_factory(admin_repo, faker):
    async def admin(i=0, email=None):
        data = {
            "email": email if email else faker.email(),
            "name": faker.name(),
            "surname": faker.name(),
            "patronymic": faker.name(),
            "birth_date": faker.date(),
            "passport_number": "123465",
            "passport_series": "9816",
            "type": "admin",
            "phone": (
                faker.phone_number()
                .replace(" ", "")
                .replace("-", "")
                .replace("(", "")
                .replace(")", "")
            ),
        }
        return await admin_repo.create(data)

    return admin


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
