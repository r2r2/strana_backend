import pytest

from pytest import mark
from tortoise.exceptions import IntegrityError


@mark.asyncio
class TestUserModel(object):
    async def test_different_role_users_with_same_credentials(
        self, client, user_factory, agent_factory, active_agency, repres_factory
    ):
        """
        Можно создавать пользователей с одними и теми же email-ами, номерами телефонов и т.п.,
        но разными типами (админ, репрез...).
        """
        data = dict(email="test@test.ru", agency_id=active_agency.id)
        await user_factory(**data)
        await agent_factory(**data)
        await repres_factory(**data)

        with pytest.raises(IntegrityError):
            await user_factory(**data)
        with pytest.raises(IntegrityError):
            await agent_factory(**data)
        with pytest.raises(IntegrityError):
            await repres_factory(**data)
