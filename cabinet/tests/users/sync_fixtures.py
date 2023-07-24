import json
from base64 import b64encode
from typing import Type

from pytz import UTC
from uuid import uuid4
from pytest import fixture
from importlib import import_module
from datetime import datetime, timedelta

from src.agents.services import EnsureBrokerTagService
from src.users.repos import NotificationMuteRepo
from src.users.services import NotificationConditionService


@fixture(scope="function")
def user_repo():
    user_repo = getattr(import_module("src.users.repos"), "UserRepo")()
    return user_repo


@fixture(scope="function")
def check_repo():
    check_repo = getattr(import_module("src.users.repos"), "CheckRepo")()
    return check_repo


@fixture(scope="function")
def notification_mute_repo(notification_mute_repo_class) -> NotificationMuteRepo:
    return notification_mute_repo_class()


@fixture(scope="function")
def notification_mute_repo_class() -> Type[NotificationMuteRepo]:
    return getattr(import_module("src.users.repos"), "NotificationMuteRepo")


@fixture(scope="function")
def user_types():
    user_types = getattr(import_module("src.users.constants"), "UserType")
    return user_types


@fixture(scope="function")
def notification_condition_service(notification_mute_repo_class) -> NotificationConditionService:
    return NotificationConditionService(notification_mute_repo=notification_mute_repo_class)


@fixture(scope="function")
def user_factory(user_repo, faker):
    async def user(agent_id=None, i=0, agency_id=None, email=None):
        data = {
            "email": email if email is not None else faker.email(),
            "name": faker.name(),
            "surname": faker.name(),
            "patronymic": faker.name(),
            "birth_date": faker.date(),
            "passport_number": "123465",
            "passport_series": "9816",
            "token": str(uuid4()),
            "code_time": datetime.now(tz=UTC),
            "code": "1234",
            "is_active": False,
            "type": "client",
            "agent_id": agent_id,
            "work_start": datetime.now().date() + timedelta(days=i),
            "work_end": datetime.now().date() + timedelta(days=i + 15),
            "phone": (
                faker.phone_number()
                .replace(" ", "")
                .replace("-", "")
                .replace("(", "")
                .replace(")", "")
            ),
            "agency_id": agency_id,
        }
        return await user_repo.create(data)

    return user


@fixture(scope="function")
def check_factory(check_repo):
    async def check(user_id, agent_id=None, status=None, agency_id=None):
        if not status:
            status = "check"
        data = {"agent_id": agent_id, "user_id": user_id, "status": status, "agency_id": agency_id}
        return await check_repo.create(data)

    return check


@fixture(scope="function")
def create_contact_service_class():
    create_contact_service_class = getattr(
        import_module("src.users.services"), "CreateContactService"
    )
    return create_contact_service_class


@fixture(scope="function")
def ensure_broker_tag_service_class() -> Type[EnsureBrokerTagService]:
    ensure_broker_tag_service_class = getattr(
        import_module("src.agents.services"), "EnsureBrokerTagService"
    )
    return ensure_broker_tag_service_class


@fixture(scope="function")
def user_authorization(user):
    token_creator = getattr(import_module("common.security"), "create_access_token")
    jwt = token_creator(user.type.value, user.id)
    authorization = f"{jwt['type'].capitalize()} {jwt['token']}"
    return authorization


@fixture(scope="function")
def agent_authorization(agent):
    token_creator = getattr(import_module("common.security"), "create_access_token")
    jwt = token_creator(agent.type.value, agent.id)
    authorization = f"{jwt['type'].capitalize()} {jwt['token']}"
    return authorization


@fixture(scope="function")
def fake_user_authorization():
    token_creator = getattr(import_module("common.security"), "create_access_token")
    jwt = token_creator("fake", 9864)
    authorization = f"{jwt['type'].capitalize()} {jwt['token']}"
    return authorization


@fixture(scope="function")
def user_token_query(user, agent, hasher) -> str:
    data = json.dumps(dict(agent_id=agent.id, client_id=user.id))
    b64_data = b64encode(data.encode()).decode()
    b64_data = b64_data.replace("&", "%26")
    token = hasher.hash(b64_data)
    url_query = f"t={token}%26d={b64_data}"

    return url_query
