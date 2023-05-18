from pytest import fixture
from importlib import import_module


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
