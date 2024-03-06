import pytest
import datetime
from pytz import UTC

from unittest.mock import AsyncMock, patch

from common.amocrm.types import AmoTag, AmoContact, AmoContactEmbedded
from common.amocrm.amocrm import AmoCRM
from src.agents.services.create_contact import CreateContactService

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


class TestAgentRegisterCase:
    async def test_check_agent_register_unmatched_password_400(self, async_client, faker):
        payload = dict(
            name=faker.name(),
            surname=faker.name(),
            patronymic=faker.name(),
            phone=f"7910{faker.random_int(min=1111111, max=9999999)}",
            password_1=faker.password(),
            password_2=faker.password(),
            email=faker.email(),
            is_contracted=False,
            agency=faker.random_int(min=111, max=999),
        )
        response = await async_client.post("/agents/register", json=payload)

        # общий ответ апи
        assert response.status_code == 400
        assert response.json()["reason"] == "agent_passwords_doesnt_match"

    async def test_check_agent_register_incorrect_phone_422(self, async_client, faker):
        payload = dict(
            name=faker.name(),
            surname=faker.name(),
            patronymic=faker.name(),
            phone="1234567890",
            password_1=faker.password(),
            password_2=faker.password(),
            email=faker.email(),
            is_contracted=False,
            agency=faker.random_int(min=111, max=999),
        )
        response = await async_client.post("/agents/register", json=payload)

        # общий ответ апи
        assert response.status_code == 422
        assert response.json()["reason"] == "agent_incorrect_phone_format"

    async def test_check_agent_register_agent_no_agency_400(self, async_client, faker):
        password = faker.password()
        payload = dict(
            name=faker.name(),
            surname=faker.name(),
            patronymic=faker.name(),
            phone=f"7910{faker.random_int(min=1111111, max=9999999)}",
            password_1=password,
            password_2=password,
            email=faker.email(),
            is_contracted=False,
            agency=faker.random_int(min=111, max=999),
        )
        response = await async_client.post("/agents/register", json=payload)

        # общий ответ апи
        assert response.status_code == 400
        assert response.json()["reason"] == "agent_no_agency"

    async def test_check_agent_register_phone_is_already_used_400(self, async_client, agent, active_agency, faker):
        password = faker.password()
        payload = dict(
            name=faker.name(),
            surname=faker.name(),
            patronymic=faker.name(),
            phone=agent.phone,
            password_1=password,
            password_2=password,
            email=faker.email(),
            is_contracted=False,
            agency=active_agency.id,
        )
        response = await async_client.post("/agents/register", json=payload)

        # общий ответ апи
        assert response.status_code == 400
        assert response.json()["reason"] == "phone_is_already_used"
        assert response.json()["message"] == (
            "Простите, данный номер телефона закреплен за другим агентом, вы не можете его использовать."
        )

    async def test_check_agent_register_email_is_already_used_400(self, async_client, agent, active_agency, faker):
        password = faker.password()
        payload = dict(
            name=faker.name(),
            surname=faker.name(),
            patronymic=faker.name(),
            phone=f"7910{faker.random_int(min=1111111, max=9999999)}",
            password_1=password,
            password_2=password,
            email=agent.email,
            is_contracted=False,
            agency=active_agency.id,
        )
        response = await async_client.post("/agents/register", json=payload)

        # общий ответ апи
        assert response.status_code == 400
        assert response.json()["reason"] == "email_is_already_used"
        assert response.json()["message"] == (
            "Простите, данная почта закреплена за другим агентом, вы не можете её использовать."
        )

    async def test_check_agent_register_phone_and_email_is_already_used_400(
        self,
        async_client,
        agent,
        active_agency,
        faker,
    ):
        password = faker.password()
        payload = dict(
            name=faker.name(),
            surname=faker.name(),
            patronymic=faker.name(),
            phone=agent.phone,
            password_1=password,
            password_2=password,
            email=agent.email,
            is_contracted=False,
            agency=active_agency.id,
        )
        response = await async_client.post("/agents/register", json=payload)

        # общий ответ апи
        assert response.status_code == 400
        assert response.json()["reason"] == "email_and_phone_is_already_used"
        assert response.json()["message"] == (
            "Простите, данная почта закреплена за другим агентом, "
            "телефон закреплен за другим агентом, вы не можете их использовать."
        )

    @patch("src.users.services.check_unique_in_base.UserCheckUniqueService.__call__", new_callable=AsyncMock)
    @patch("src.agents.use_cases.process_register.ProcessRegisterCase._import_contacts", new_callable=AsyncMock)
    @patch("src.agents.use_cases.process_register.ProcessRegisterCase._send_confirm_email", new_callable=AsyncMock)
    @patch("src.agents.use_cases.process_register.ProcessRegisterCase._send_agency_email", new_callable=AsyncMock)
    @patch("common.security.create_email_token")
    async def test_check_agent_register_delete_old_agent(
        self,
        mock_create_email_token_util,
        mock_send_agency_email,
        mock_send_confirm_email,
        mock_import_contacts,
        mock_check_unique_in_base,
        async_client,
        active_agency,
        agent_role,
        user_repo,
        agent_for_deleting,
        faker,
    ):
        mock_create_email_token_util.return_value = faker.word()

        password = faker.password()
        payload = dict(
            name=faker.name(),
            surname=faker.name(),
            patronymic=faker.name(),
            phone=f"7910{faker.random_int(min=1111111, max=9999999)}",
            password_1=password,
            password_2=password,
            email=agent_for_deleting.email,
            is_contracted=False,
            agency=active_agency.id,
        )
        response = await async_client.post("/agents/register", json=payload)

        # получаем данные из тестовой БД для проверки
        created_agent = await user_repo.retrieve(filters=dict(email=payload["email"], role_id=agent_role.id))
        deleted_agent = await user_repo.retrieve(filters=dict(id=agent_for_deleting.id))

        # общий ответ апи
        assert response.status_code == 201
        assert response.json()["id"] == created_agent.id
        assert response.json()["is_approved"] == created_agent.is_approved
        # проверяем, что агент с отметкой об удалении был действительно удален
        assert not deleted_agent

    @patch("src.users.services.check_unique_in_base.UserCheckUniqueService.__call__", new_callable=AsyncMock)
    @patch("src.agents.use_cases.process_register.ProcessRegisterCase._send_confirm_email", new_callable=AsyncMock)
    @patch("src.agents.use_cases.process_register.ProcessRegisterCase._send_agency_email", new_callable=AsyncMock)
    @patch("common.security.create_email_token")
    @patch("common.amocrm.components.contacts.AmoCRMContacts.fetch_contacts", new_callable=AsyncMock)
    @patch("common.amocrm.components.contacts.AmoCRMContacts.create_contact", new_callable=AsyncMock)
    @patch("common.amocrm.components.contacts.AmoCRMContacts.update_contact", new_callable=AsyncMock)
    @patch("common.amocrm.services.bind_contact_to_company.BindContactCompanyService.__call__", new_callable=AsyncMock)
    @patch("celery.app.task.Task.delay")
    @patch("common.amocrm.amocrm.AmoCRM.__aexit__", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__ainit__", new_callable=AsyncMock)
    async def test_check_agent_register_no_contact_in_amo(
        self,
        mock_amocrm_ainit,
        mock_amocrm_aexit,
        mock_import_clients_task,
        mock_bind_contact_to_company_service,
        mock_amo_update_contact,
        mock_amo_create_contact,
        mock_amo_fetch_contacts,
        mock_create_email_token_util,
        mock_send_agency_email,
        mock_send_confirm_email,
        mock_check_unique_in_base,
        async_client,
        active_agency,
        agent_role,
        user_repo,
        faker,
    ):
        mock_create_email_token_util.return_value = faker.word()
        mock_amo_fetch_contacts.return_value = []
        mock_amo_create_contact.return_value = [{"id": faker.random_int(min=1111111, max=9999999)}]

        password = faker.password()
        payload = dict(
            name=faker.name(),
            surname=faker.name(),
            patronymic=faker.name(),
            phone=f"7910{faker.random_int(min=1111111, max=9999999)}",
            password_1=password,
            password_2=password,
            email=faker.email(),
            is_contracted=False,
            agency=active_agency.id,
        )
        response = await async_client.post("/agents/register", json=payload)

        # получаем данные из тестовой БД для проверки
        created_agent = await user_repo.retrieve(
            filters=dict(email=payload["email"], role_id=agent_role.id),
            related_fields=["agency"],
        )

        # общий ответ апи
        assert response.status_code == 201
        assert response.json()["id"] == created_agent.id
        assert response.json()["is_approved"] == created_agent.is_approved
        # проверяем, что для контакта был создан amocrm_id и теги
        assert created_agent.amocrm_id == mock_amo_create_contact.return_value[0]["id"]
        assert created_agent.tags
        assert created_agent.is_imported is True

        # проверка вызова замоканых функций/сервисов
        mock_amo_fetch_contacts.assert_called_once_with(user_phone=created_agent.phone)
        mock_amo_create_contact.assert_called_once_with(
            user_phone=created_agent.phone,
            tags=CreateContactService.lk_broker_tags,
        )
        mock_amo_update_contact.assert_called_once_with(
            user_id=created_agent.amocrm_id,
            user_tags=
            [
                tag.dict(exclude_none=True) for tag in [
                    AmoTag(name=CreateContactService.lk_broker_tag),
                    AmoTag(name=AmoCRM.broker_tag),
                ]
            ],
            user_email=created_agent.email,
            user_company=created_agent.agency.amocrm_id,
            user_name=f"{created_agent.surname} {created_agent.name} {created_agent.patronymic}",
        )
        mock_bind_contact_to_company_service.assert_called_once_with(
            agent_amocrm_id=created_agent.amocrm_id,
            agency_amocrm_id=created_agent.agency.amocrm_id,
        )
        mock_import_clients_task.assert_called_once_with(agent_id=created_agent.id)
        mock_amocrm_ainit.assert_called_once()
        mock_amocrm_aexit.assert_called_once()

    @patch("src.users.services.check_unique_in_base.UserCheckUniqueService.__call__", new_callable=AsyncMock)
    @patch("src.agents.use_cases.process_register.ProcessRegisterCase._send_confirm_email", new_callable=AsyncMock)
    @patch("src.agents.use_cases.process_register.ProcessRegisterCase._send_agency_email", new_callable=AsyncMock)
    @patch("common.security.create_email_token")
    @patch("common.amocrm.components.contacts.AmoCRMContacts.fetch_contacts", new_callable=AsyncMock)
    @patch("common.amocrm.components.contacts.AmoCRMContacts.update_contact", new_callable=AsyncMock)
    @patch("common.amocrm.services.bind_contact_to_company.BindContactCompanyService.__call__", new_callable=AsyncMock)
    @patch("celery.app.task.Task.delay")
    @patch("common.amocrm.amocrm.AmoCRM.__aexit__", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__ainit__", new_callable=AsyncMock)
    async def test_check_agent_register_one_contact_in_amo(
        self,
        mock_amocrm_ainit,
        mock_amocrm_aexit,
        mock_import_clients_task,
        mock_bind_contact_to_company_service,
        mock_amo_update_contact,
        mock_amo_fetch_contacts,
        mock_create_email_token_util,
        mock_send_agency_email,
        mock_send_confirm_email,
        mock_check_unique_in_base,
        async_client,
        active_agency,
        agent_role,
        user_repo,
        faker,
    ):
        mock_create_email_token_util.return_value = faker.word()
        mock_amo_fetch_contacts.return_value = [
            AmoContact(
                id=faker.random_int(min=1111111, max=9999999),
                created_at=int(datetime.datetime.now(tz=UTC).timestamp()),
                updated_at=int(datetime.datetime.now(tz=UTC).timestamp()),
                _embedded=AmoContactEmbedded(tags=[]),
            ),
        ]

        password = faker.password()
        payload = dict(
            name=faker.name(),
            surname=faker.name(),
            patronymic=faker.name(),
            phone=f"7910{faker.random_int(min=1111111, max=9999999)}",
            password_1=password,
            password_2=password,
            email=faker.email(),
            is_contracted=False,
            agency=active_agency.id,
        )
        response = await async_client.post("/agents/register", json=payload)

        # получаем данные из тестовой БД для проверки
        created_agent = await user_repo.retrieve(
            filters=dict(email=payload["email"], role_id=agent_role.id),
            related_fields=["agency"],
        )

        # общий ответ апи
        assert response.status_code == 201
        assert response.json()["id"] == created_agent.id
        assert response.json()["is_approved"] == created_agent.is_approved
        # проверяем, что для контакта был создан amocrm_id и теги
        assert created_agent.amocrm_id == mock_amo_fetch_contacts.return_value[0].id
        assert created_agent.tags
        assert created_agent.is_imported is True

        # проверка вызова замоканых функций/сервисов
        mock_check_unique_in_base.assert_called_once()
        mock_amo_fetch_contacts.assert_called_once_with(user_phone=created_agent.phone)
        mock_amo_update_contact.assert_called_once_with(
            user_id=created_agent.amocrm_id,
            user_tags=[tag.dict(exclude_none=True) for tag in [AmoTag(name=AmoCRM.broker_tag)]],
            user_email=created_agent.email,
            user_company=created_agent.agency.amocrm_id,
            user_name=f"{created_agent.surname} {created_agent.name} {created_agent.patronymic}",
        )
        mock_bind_contact_to_company_service.assert_called_once_with(
            agent_amocrm_id=created_agent.amocrm_id,
            agency_amocrm_id=created_agent.agency.amocrm_id,
        )
        mock_import_clients_task.assert_called_once_with(agent_id=created_agent.id)
        mock_create_email_token_util.assert_called_once_with(created_agent.id)
        mock_send_confirm_email.assert_called_once_with(
            agent=created_agent,
            token=mock_create_email_token_util.return_value,
        )
        mock_send_agency_email.assert_called_once_with(
            agent=created_agent,
            agency=active_agency,
        )
        mock_amocrm_ainit.assert_called_once()
        mock_amocrm_aexit.assert_called_once()
