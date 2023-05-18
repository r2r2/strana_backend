import pytest
from httpx import Response

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


class TestSendCodeAuthCase:
    test_phone: str = "+79304098405"
    headers: dict = {"x-real-ip": "102.127.38.40"}
    async def test_send_code_success(self, async_client, faker, user_repo):
        data: dict = dict(phone=self.test_phone)
        send_code_result: Response = await async_client.post("/users/send_code", json=data, headers=self.headers)
        user = await user_repo.retrieve(filters=dict(phone=self.test_phone))
        assert send_code_result.status_code == 200
        assert user.phone == self.test_phone, "Номер телефона не совпадает"
        response_token: str = send_code_result.json().get("token")
        assert response_token == str(user.token), "Токен не совпадает"

    # async def test_send_code_and_validate__success(self, async_client, faker, user_repo):
    #     data: dict = dict(phone=self.test_phone)
    #     send_code_result: Response = await async_client.post("/users/send_code", json=data, headers=self.headers)
    #     user = await user_repo.retrieve(filters=dict(phone=self.test_phone))
    #     assert send_code_result.status_code == 200
    #     code: str = user.code
    #     token: str = send_code_result.json().get("token")
    #     data: dict = dict(
    #         phone=self.test_phone,
    #         token=token,
    #         code=code
    #     )
    #     res = await async_client.post("/users/validate_code", json=data, headers=self.headers)
    #     assert res.status_code == 200
