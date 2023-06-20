from pytest import fixture
from secrets import token_urlsafe
from importlib import import_module


@fixture(scope="function")
def repres_repo():
    repres_repo = getattr(import_module("src.represes.repos"), "RepresRepo")()
    return repres_repo


@fixture(scope="function")
def repres_authorization(repres):
    token_creator = getattr(import_module("common.security"), "create_access_token")
    jwt = token_creator(repres.type.value, repres.id, {"agency_id": repres.agency_id})
    authorization = f"{jwt['type'].capitalize()} {jwt['token']}"
    return authorization


@fixture(scope="function")
def repres_factory(repres_repo, faker):
    async def repres(agency_id=None, i=0, maintained_id=None, email=None):
        data = {
            "email": email if email else faker.email(),
            "name": faker.name(),
            "surname": faker.name(),
            "patronymic": faker.name(),
            "birth_date": faker.date(),
            "passport_number": "123465",
            "passport_series": "9816",
            "type": "repres",
            "agency_id": agency_id,
            "maintained_id": maintained_id,
            "phone": (
                faker.phone_number()
                .replace(" ", "")
                .replace("-", "")
                .replace("(", "")
                .replace(")", "")
            ),
        }
        return await repres_repo.create(data)

    return repres


@fixture(scope="function")
async def repres(repres_repo, active_agency):
    data = {
        "name": "test",
        "type": "repres",
        "is_active": True,
        "surname": "string",
        "is_approved": True,
        "patronymic": "string",
        "email": "testtest_email@email.com",
        "email_token": token_urlsafe(32),
        "duty_type": "director",
        "agency_id": active_agency.id,
        "maintained_id": active_agency.id,
    }
    repres = await repres_repo.update_or_create({"phone": "+79296010019"}, data)
    return repres
