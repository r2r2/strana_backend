import pytest
import datetime
from pytz import UTC

from unittest.mock import AsyncMock, patch, call

from common.amocrm.constants import AmoContactQueryWith
from common.amocrm.types.contact import AmoContact, AmoContactEmbedded
from common.amocrm.types.lead import AmoLead
from src.users.use_cases import AssignClientCase
from src.users.constants import UserPinningStatusType
from src.booking.constants import BookingStages, BookingSubstages, BookingCreatedSources

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


class TestClientCheckUniqueCase:
    @patch("common.dependencies.users.DeletedUserCheck.__call__", new_callable=AsyncMock)
    async def test_check_client_unique_by_client_403(self, mock_delete_user_check, async_client, user_authorization):
        headers = {"Authorization": user_authorization}
        response = await async_client.post("v2/users/agent/check", headers=headers)
        assert response.status_code == 403

    @patch("common.dependencies.users.DeletedUserCheck.__call__", new_callable=AsyncMock)
    async def test_check_client_unique_user_miss_match_400(
        self,
        mock_delete_user_check,
        async_client,
        agent_authorization,
        user,
        faker,
    ):
        headers = {"Authorization": agent_authorization}
        payload = dict(
            phone=f"+7910{faker.random_int(min=1111111, max=9999999)}",
            email=user.email,
            name=faker.name(),
            surname=faker.name(),
            patronymic=faker.name(),
        )
        response = await async_client.post("/v2/users/agent/check", headers=headers, json=payload)

        # общий ответ апи
        assert response.status_code == 400
        assert response.json()["reason"] == "user_miss_match"

    @patch("common.dependencies.users.DeletedUserCheck.__call__", new_callable=AsyncMock)
    @patch("src.users.services.check_unique_v2.CheckUniqueServiceV2.__call__", new_callable=AsyncMock)
    async def test_check_client_unique_create_user(
        self,
        mock_check_unique_v2_service,
        mock_delete_user_check,
        async_client,
        agent_authorization,
        user_repo,
        faker,
    ):
        mock_check_unique_v2_service.return_value = None, []

        headers = {"Authorization": agent_authorization}
        payload = dict(
            phone=f"+7929{faker.random_int(min=1111111, max=9999999)}",
            email=faker.email(),
            name=faker.name(),
            surname=faker.name(),
            patronymic=faker.name(),
        )
        response = await async_client.post("/v2/users/agent/check", headers=headers, json=payload)

        # получаем данные из тестовой БД для проверки
        user = await user_repo.retrieve(filters=dict(phone=payload["phone"]))

        # общий ответ апи
        assert response.status_code == 200
        assert response.json()["userId"] == user.id

    @patch("common.dependencies.users.DeletedUserCheck.__call__", new_callable=AsyncMock)
    @patch("src.users.services.check_unique_v2.CheckUniqueServiceV2.__call__", new_callable=AsyncMock)
    async def test_check_client_unique_with_existed_fixed_check_404(
        self,
        mock_check_unique_v2_service,
        mock_delete_user_check,
        async_client,
        agent_authorization,
        user_for_checking,
        user_fixed_check,
        faker,
    ):
        mock_check_unique_v2_service.return_value = None, []

        headers = {"Authorization": agent_authorization}
        payload = dict(
            phone=user_for_checking.phone,
            email=user_for_checking.email,
            name=user_for_checking.name,
            surname=user_for_checking.surname,
            patronymic=user_for_checking.patronymic,
        )
        response = await async_client.post("/v2/users/agent/check", headers=headers, json=payload)

        # общий ответ апи
        assert response.status_code == 404
        assert response.json()["reason"] == "unique_status_button_not_found"

    @patch("common.dependencies.users.DeletedUserCheck.__call__", new_callable=AsyncMock)
    @patch("src.users.services.check_unique_v2.CheckUniqueServiceV2.__call__", new_callable=AsyncMock)
    async def test_check_client_unique_with_existed_fixed_check(
        self,
        mock_check_unique_v2_service,
        mock_delete_user_check,
        async_client,
        agent,
        agent_authorization,
        user_for_checking,
        user_fixed_check,
        check_history_repo,
        unique_status_button,
        faker,
    ):
        mock_check_unique_v2_service.return_value = None, []

        headers = {"Authorization": agent_authorization}
        payload = dict(
            phone=user_for_checking.phone,
            email=user_for_checking.email,
            name=user_for_checking.name,
            surname=user_for_checking.surname,
            patronymic=user_for_checking.patronymic,
        )
        response = await async_client.post("/v2/users/agent/check", headers=headers, json=payload)

        # получаем данные из тестовой БД для проверки
        check_history = await check_history_repo.retrieve(
            filters=dict(
                agent_id=agent.id,
                agency_id=agent.agency_id,
                client_phone=payload["phone"],
            ),
        )

        # общий ответ апи
        assert response.status_code == 200
        assert response.json()["id"] == user_fixed_check.id
        assert response.json()["userId"] == user_for_checking.id
        assert response.json()["button"]["text"] == unique_status_button.text

        # проверка созданной истории проверки
        assert check_history.agent_id == agent.id
        assert check_history.agency_id == agent.agency_id
        assert check_history.client_phone == payload["phone"]
        assert check_history.lead_link

        # проверка вызова замоканых функций/сервисов
        mock_check_unique_v2_service.assert_not_called()

    @patch("common.dependencies.users.DeletedUserCheck.__call__", new_callable=AsyncMock)
    @patch("src.users.services.check_unique_v2.CheckUniqueServiceV2.__call__", new_callable=AsyncMock)
    @patch("src.users.services.send_check_admins_email.SendCheckAdminsEmailService.__call__", new_callable=AsyncMock)
    async def test_check_client_unique_with_existed_check(
        self,
        mock_send_check_admins_email_service,
        mock_check_unique_v2_service,
        mock_delete_user_check,
        async_client,
        agent_authorization,
        user_for_checking,
        user_not_fixed_check,
        faker,
    ):
        mock_check_unique_v2_service.return_value = None, []

        headers = {"Authorization": agent_authorization}
        payload = dict(
            phone=user_for_checking.phone,
            email=user_for_checking.email,
            name=user_for_checking.name,
            surname=user_for_checking.surname,
            patronymic=user_for_checking.patronymic,
        )
        response = await async_client.post("/v2/users/agent/check", headers=headers, json=payload)

        # общий ответ апи
        assert response.status_code == 200
        assert response.json()["id"] == user_not_fixed_check.id
        assert response.json()["userId"] == user_for_checking.id

        # проверка вызова замоканых функций/сервисов
        mock_send_check_admins_email_service.assert_called()

    @patch("common.dependencies.users.DeletedUserCheck.__call__", new_callable=AsyncMock)
    @patch("src.users.services.check_unique_v2.CheckUniqueServiceV2.__call__", new_callable=AsyncMock)
    async def test_check_client_unique_by_repres(
        self,
        mock_check_unique_v2_service,
        mock_delete_user_check,
        async_client,
        repres_for_assign,
        repres_authorization_for_assign,
        user_for_checking,
        check_history_repo,
        faker,
    ):
        mock_check_unique_v2_service.return_value = None, []

        headers = {"Authorization": repres_authorization_for_assign}
        payload = dict(
            phone=user_for_checking.phone,
            email=user_for_checking.email,
            name=user_for_checking.name,
            surname=user_for_checking.surname,
            patronymic=user_for_checking.patronymic,
        )
        response = await async_client.post("/v2/users/repres/check", headers=headers, json=payload)

        # получаем данные из тестовой БД для проверки
        check_history = await check_history_repo.retrieve(
            filters=dict(
                agency_id=repres_for_assign.agency_id,
                client_phone=payload["phone"],
            ),
        )

        # общий ответ апи
        assert response.status_code == 200

        # проверка созданной истории проверки
        assert check_history.agency_id == repres_for_assign.agency_id
        assert check_history.client_phone == payload["phone"]

    @patch("common.dependencies.users.DeletedUserCheck.__call__", new_callable=AsyncMock)
    @patch("src.users.services.check_unique_v2.CheckUniqueServiceV2.__call__", new_callable=AsyncMock)
    async def test_check_client_unique(
        self,
        mock_check_unique_v2_service,
        mock_delete_user_check,
        async_client,
        agent,
        agent_authorization,
        user_for_checking,
        check_repo,
        check_history_repo,
        amocrm_check_log_repo,
        amocrm_check_log,
        faker,
    ):
        mock_check_unique_v2_service.return_value = None, [amocrm_check_log.id]

        headers = {"Authorization": agent_authorization}
        payload = dict(
            phone=user_for_checking.phone,
            email=user_for_checking.email,
            name=user_for_checking.name,
            surname=user_for_checking.surname,
            patronymic=user_for_checking.patronymic,
        )
        response = await async_client.post("/v2/users/agent/check", headers=headers, json=payload)

        # получаем данные из тестовой БД для проверки
        check = await check_repo.retrieve(filters=dict(user_id=user_for_checking.id))
        check_history = await check_history_repo.retrieve(
            filters=dict(
                agent_id=agent.id,
                agency_id=agent.agency_id,
                client_phone=payload["phone"],
            ),
        )
        updated_amo_crm_check_log = await amocrm_check_log_repo.retrieve(filters=dict(id=amocrm_check_log.id))

        # общий ответ апи
        assert response.status_code == 200
        # проверка созданной истории проверки
        assert check_history.agent_id == agent.id
        assert check_history.agency_id == agent.agency_id
        assert check_history.client_phone == payload["phone"]
        # проверяем обновленные логи запросов истории проверки в AmoCrm
        assert updated_amo_crm_check_log.check_history_id == check_history.id

        # проверка вызова замоканых функций/сервисов с сигнатурой
        mock_check_unique_v2_service.assert_called_once_with(
            phone=user_for_checking.phone,
            check=check,
            user=user_for_checking,
            agent_id=str(agent.id),
            agency_id=None,
        )
