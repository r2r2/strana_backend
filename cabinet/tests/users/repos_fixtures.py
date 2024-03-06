import pytest
from importlib import import_module

from src.agencies.repos import AgencyGeneralTypeRepo
from src.tips.repos import TipRepo
from src.users.repos import (
    UserRepo,
    UserRoleRepo,
    ConsultationTypeRepo,
    UniqueStatusRepo,
    UserPinningStatusRepo,
    ConfirmClientAssignRepo,
    CheckRepo,
    ClientAssignMaintenanceRepo,
    CheckHistoryRepo,
    UniqueStatusButtonRepo,
    AmoCrmCheckLogRepo,
    CheckTermRepo,
)


@pytest.fixture(scope="function")
def tips_repo() -> TipRepo:
    tips_repo: TipRepo = getattr(import_module("src.tips.repos"), "TipRepo")()
    return tips_repo


@pytest.fixture(scope="function")
def fake_tip(faker) -> dict:
    return dict(
        image=faker.image(size=(1, 1)),
        title=faker.word(),
        text=faker.text(),
        order=faker.numerify()
    )


@pytest.fixture(scope="function")
def user_repo() -> UserRepo:
    user_repo: UserRepo = getattr(import_module("src.users.repos"), "UserRepo")()
    return user_repo


@pytest.fixture(scope="function")
def user_role_repo() -> UserRoleRepo:
    user_role_repo: UserRoleRepo = getattr(import_module("src.users.repos"), "UserRoleRepo")()
    return user_role_repo


@pytest.fixture(scope="function")
def general_type_repo() -> AgencyGeneralTypeRepo:
    general_type_repo: AgencyGeneralTypeRepo = getattr(import_module("src.agencies.repos"), "AgencyGeneralTypeRepo")()
    return general_type_repo


@pytest.fixture(scope="function")
def consultation_type_repo() -> ConsultationTypeRepo:
    consultation_type_repo: ConsultationTypeRepo = getattr(import_module("src.users.repos"), "ConsultationTypeRepo")()
    return consultation_type_repo


@pytest.fixture(scope="function")
def unique_status_repo() -> UniqueStatusRepo:
    unique_status_repo: UniqueStatusRepo = getattr(import_module("src.users.repos"), "UniqueStatusRepo")()
    return unique_status_repo


@pytest.fixture(scope="function")
def user_pinning_status_repo() -> UserPinningStatusRepo:
    user_pinning_status_repo: UserPinningStatusRepo = getattr(
        import_module("src.users.repos"),
        "UserPinningStatusRepo",
    )()
    return user_pinning_status_repo


@pytest.fixture(scope="function")
def confirm_client_assign_repo() -> ConfirmClientAssignRepo:
    confirm_client_assign_repo: ConfirmClientAssignRepo = getattr(
        import_module("src.users.repos"),
        "ConfirmClientAssignRepo",
    )()
    return confirm_client_assign_repo


@pytest.fixture(scope="function")
def check_repo() -> CheckRepo:
    check_repo: CheckRepo = getattr(import_module("src.users.repos"), "CheckRepo")()
    return check_repo


@pytest.fixture(scope="function")
def client_assign_maintenance_repo() -> ClientAssignMaintenanceRepo:
    check_repo: ClientAssignMaintenanceRepo = getattr(import_module("src.users.repos"), "ClientAssignMaintenanceRepo")()
    return check_repo


@pytest.fixture(scope="function")
def check_history_repo() -> CheckHistoryRepo:
    check_history_repo: CheckHistoryRepo = getattr(import_module("src.users.repos"), "CheckHistoryRepo")()
    return check_history_repo


@pytest.fixture(scope="function")
def unique_status_button_repo() -> UniqueStatusButtonRepo:
    unique_status_button_repo: UniqueStatusButtonRepo = getattr(
        import_module("src.users.repos"),
        "UniqueStatusButtonRepo",
    )()
    return unique_status_button_repo


@pytest.fixture(scope="function")
def amocrm_check_log_repo() -> AmoCrmCheckLogRepo:
    amo_crm_check_log_repo: AmoCrmCheckLogRepo = getattr(import_module("src.users.repos"), "AmoCrmCheckLogRepo")()
    return amo_crm_check_log_repo


@pytest.fixture(scope="function")
def check_term_repo() -> CheckTermRepo:
    check_term_repo: CheckTermRepo = getattr(import_module("src.users.repos"), "CheckTermRepo")()
    return check_term_repo
