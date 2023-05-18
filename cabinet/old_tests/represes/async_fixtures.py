from pytest import fixture
from secrets import token_urlsafe


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
