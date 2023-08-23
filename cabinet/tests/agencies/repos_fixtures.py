from importlib import import_module

from pytest import fixture

from src.agreements.repos import AgencyAgreementRepo, AgreementTypeRepo, AgreementStatus, AgencyAgreement, AgreementType


@fixture(scope="function")
def agreement_repo() -> AgencyAgreementRepo:
    agreement_repo: AgencyAgreementRepo = getattr(
        import_module("src.agreements.repos"), "AgencyAgreementRepo"
    )()
    return agreement_repo


@fixture(scope="function")
def agreement_type_repo() -> AgreementTypeRepo:
    agreement_type_repo: AgreementTypeRepo = getattr(
        import_module("src.agreements.repos"), "AgreementTypeRepo"
    )()
    return agreement_type_repo


@fixture(scope="function")
async def agreement_type(agreement_type_repo, faker) -> AgreementType:
    data = {
        "name": f"test_{faker.word()}",
        "description": faker.text(),
        "priority": 100,
    }
    agreement_type: AgreementType = await agreement_type_repo.create(data)
    return agreement_type


@fixture(scope="function")
async def agreement_status(faker) -> AgreementStatus:
    data = {
        "name": f"test_{faker.word()}",
        "description": faker.text(),
    }
    status = await AgreementStatus.create(**data)
    return status


@fixture(scope="function")
async def agreement(
    faker,
    agreement_repo,
    agreement_type,
    active_agency,
    booking,
    project,
    agreement_status,
) -> AgencyAgreement:
    data = {
        "project_id": project.id,
        "agency_id": active_agency.id,
        "agreement_type_id": agreement_type.id,
        "booking_id": booking.id,
        "number": faker.bothify(letters="ABCDE"),
        "status_id": agreement_status.id,
        "template_name": "Договор",
        "files": [{"name": "Договор", "slug": "agreement_file", "count": 1, "files": [{"aws": "https://storage.yandexcloud.net/", "kb_size": 53.6, "mb_size": 0.1, "extension": "docx", "bytes_size": 54881, "content_type": ""}]}],
    }
    agreement = await agreement_repo.create(data)
    return agreement
