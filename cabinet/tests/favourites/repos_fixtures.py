import pytest
from importlib import import_module

from src.users.repos import UserViewedProperty, UserViewedPropertyRepo


@pytest.fixture(scope="function")
def user_favorite_repo() -> UserViewedPropertyRepo:
    user_favorite_repo: UserViewedPropertyRepo = getattr(import_module("src.users.repos"), "UserViewedPropertyRepo")()
    return user_favorite_repo


@pytest.fixture(scope="function")
async def user_favorite_factory(
        user_favorite_repo, user, property
) -> UserViewedProperty:
    user_favorite: UserViewedProperty = await user_favorite_repo.create(
        data=dict(
            client_id=user.id,
            property_id=property.id,
        )
    )
    return user_favorite
