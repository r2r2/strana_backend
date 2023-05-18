import pytest
from importlib import import_module

from src.tips.repos import TipRepo
from src.users.repos import UserRepo


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
    property_repo: UserRepo = getattr(import_module("src.users.repos"), "UserRepo")()
    return property_repo

