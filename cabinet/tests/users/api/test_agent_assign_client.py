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


class TestAgentAssignClientCase:
    @patch("common.dependencies.users.DeletedUserCheck.__call__", new_callable=AsyncMock)
    async def test_assign_client_by_client_403(self, mock_delete_user_check, async_client, user_authorization):
        headers = {"Authorization": user_authorization}
        response = await async_client.post("/users/agent/assign_client", headers=headers)
        assert response.status_code == 403

    @patch("common.dependencies.users.DeletedUserCheck.__call__", new_callable=AsyncMock)
    async def test_email_already_taken_400(
        self,
        mock_delete_user_check,
        async_client,
        agent,
        agent_authorization,
        user,
        assigned_user,
        consultation_type,
        faker,
    ):
        headers = {"Authorization": agent_authorization}
        payload = dict(
            name=assigned_user.name,
            phone=assigned_user.phone,
            email=user.email,
            check_id=faker.random_int(min=1, max=9999),
            consultation_type=consultation_type.slug,
        )
        response = await async_client.post("/users/agent/assign_client", headers=headers, json=payload)

        # общий ответ апи
        assert response.status_code == 400
        assert response.json()["reason"] == "user_email_taken"

    @patch("common.dependencies.users.DeletedUserCheck.__call__", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase._check_user_is_unique", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase._send_email", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase._amocrm_hook", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase._notify_client_sms", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase.generate_unassign_link")
    async def test_assign_client_unique_status_not_found_404(
        self,
        mock_generate_unassign_link,
        mock_notify_client_sms,
        mock_amocrm_hook,
        mock_send_email,
        mock_check_user_is_unique,
        mock_delete_user_check,
        async_client,
        agent,
        agent_authorization,
        assigned_user,
        consultation_type,
        faker,
    ):
        mock_generate_unassign_link.return_value = faker.url()
        mock_amocrm_hook.return_value = faker.random_int(min=1, max=99)

        headers = {"Authorization": agent_authorization}
        payload = dict(
            name=assigned_user.name,
            phone=assigned_user.phone,
            user_id=assigned_user.id,
            check_id=faker.random_int(min=1, max=9999),
            consultation_type=consultation_type.slug,
        )
        response = await async_client.post("/users/agent/assign_client", headers=headers, json=payload)

        # общий ответ апи
        assert response.status_code == 404
        assert response.json()["reason"] == "unique_status_not_found"

    @patch("common.dependencies.users.DeletedUserCheck.__call__", new_callable=AsyncMock)
    async def test_assign_client_check_not_found_404(
        self,
        mock_delete_user_check,
        async_client,
        agent,
        agent_authorization,
        assigned_user,
        consultation_type,
        faker,
    ):
        headers = {"Authorization": agent_authorization}
        payload = dict(
            name=assigned_user.name,
            phone=assigned_user.phone,
            user_id=assigned_user.id,
            check_id=faker.random_int(min=1, max=9999),
            consultation_type=consultation_type.slug,
        )
        response = await async_client.post("/users/agent/assign_client", headers=headers, json=payload)

        # общий ответ апи
        assert response.status_code == 404
        assert response.json()["reason"] == "check_not_found"

    @patch("common.dependencies.users.DeletedUserCheck.__call__", new_callable=AsyncMock)
    async def test_assign_client_not_unique_403(
            self,
            mock_delete_user_check,
            async_client,
            agent,
            agent_authorization,
            assigned_user,
            consultation_type,
            not_unique_user_check,
            faker,
    ):
        headers = {"Authorization": agent_authorization}
        payload = dict(
            name=assigned_user.name,
            phone=assigned_user.phone,
            user_id=assigned_user.id,
            check_id=not_unique_user_check.id,
            consultation_type=consultation_type.slug,
        )
        response = await async_client.post("/users/agent/assign_client", headers=headers, json=payload)

        # общий ответ апи
        assert response.status_code == 403
        assert response.json()["reason"] == "User is not unique"

    @patch("common.dependencies.users.DeletedUserCheck.__call__", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase._send_email", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase._amocrm_hook", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase._notify_client_sms", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase.generate_unassign_link")
    @patch("common.amocrm.components.notes.AmoCRMNotes.send_contact_note", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__ainit__", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__aexit__", new_callable=AsyncMock)
    async def test_assign_client_by_id(
        self,
        mock_amocrm_aexit,
        mock_amocrm_ainit,
        mock_amocrm_send_contact_note,
        mock_generate_unassign_link,
        mock_notify_client_sms,
        mock_amocrm_hook,
        mock_send_email,
        mock_delete_user_check,
        async_client,
        agent,
        agent_authorization,
        assigned_user,
        consultation_type,
        unique_status_partially_pinned,
        unique_user_check,
        faker,
    ):
        mock_generate_unassign_link.return_value = faker.url()
        mock_amocrm_hook.return_value = faker.random_int(min=1, max=99)
        mock_amocrm_send_contact_note.return_value = dict(
            route=faker.url(),
            status=200,
            request_data=faker.word(),
            data=faker.word(),
        )

        headers = {"Authorization": agent_authorization}
        payload = dict(
            name=assigned_user.name,
            phone=assigned_user.phone,
            user_id=assigned_user.id,
            check_id=unique_user_check.id,
            consultation_type=consultation_type.slug,
        )
        response = await async_client.post("/users/agent/assign_client", headers=headers, json=payload)

        # общий ответ апи
        assert response.status_code == 200
        assert response.json()["client_id"] == assigned_user.id
        assert response.json()["agent_id"] == agent.id
        assert response.json()["agency_id"] == agent.agency_id
        assert response.json()["bookingId"] == mock_amocrm_hook.return_value

    @patch("common.dependencies.users.DeletedUserCheck.__call__", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase._send_email", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase._amocrm_hook", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase._notify_client_sms", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase.generate_unassign_link")
    @patch("common.amocrm.components.notes.AmoCRMNotes.send_contact_note", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__ainit__", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__aexit__", new_callable=AsyncMock)
    async def test_assign_client_by_user_data(
        self,
        mock_amocrm_aexit,
        mock_amocrm_ainit,
        mock_amocrm_send_contact_note,
        mock_generate_unassign_link,
        mock_notify_client_sms,
        mock_amocrm_hook,
        mock_send_email,
        mock_delete_user_check,
        async_client,
        agent,
        agent_authorization,
        assigned_user,
        consultation_type,
        unique_status_partially_pinned,
        unique_user_check,
        faker,
    ):
        mock_generate_unassign_link.return_value = faker.url()
        mock_amocrm_hook.return_value = faker.random_int(min=1, max=99)
        mock_amocrm_send_contact_note.return_value = dict(
            route=faker.url(),
            status=200,
            request_data=faker.word(),
            data=faker.word(),
        )

        headers = {"Authorization": agent_authorization}
        payload = dict(
            name=assigned_user.name,
            phone=assigned_user.phone,
            check_id=unique_user_check.id,
            consultation_type=consultation_type.slug,
        )
        response = await async_client.post("/users/agent/assign_client", headers=headers, json=payload)

        # общий ответ апи
        assert response.status_code == 200
        assert response.json()["client_id"] == assigned_user.id
        assert response.json()["agent_id"] == agent.id
        assert response.json()["agency_id"] == agent.agency_id
        assert response.json()["bookingId"] == mock_amocrm_hook.return_value

    @patch("common.dependencies.users.DeletedUserCheck.__call__", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase._send_email", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase._amocrm_hook", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase._notify_client_sms", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase.generate_unassign_link")
    @patch("common.amocrm.components.notes.AmoCRMNotes.send_contact_note", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__ainit__", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__aexit__", new_callable=AsyncMock)
    async def test_assign_client_payload_agency_contact(
        self,
        mock_amocrm_aexit,
        mock_amocrm_ainit,
        mock_amocrm_send_contact_note,
        mock_generate_unassign_link,
        mock_notify_client_sms,
        mock_amocrm_hook,
        mock_send_email,
        mock_delete_user_check,
        async_client,
        agent,
        agent_authorization,
        assigned_user,
        consultation_type,
        unique_status_partially_pinned,
        unique_user_check,
        faker,
    ):
        mock_generate_unassign_link.return_value = faker.url()
        mock_amocrm_hook.return_value = faker.random_int(min=1, max=99)
        mock_amocrm_send_contact_note.return_value = dict(
            route=faker.url(),
            status=200,
            request_data=faker.word(),
            data=faker.word(),
        )

        headers = {"Authorization": agent_authorization}
        payload = dict(
            name=assigned_user.name,
            phone=assigned_user.phone,
            user_id=assigned_user.id,
            agency_contact=faker.word(),
            check_id=unique_user_check.id,
            consultation_type=consultation_type.slug,
        )
        response = await async_client.post("/users/agent/assign_client", headers=headers, json=payload)

        # общий ответ апи
        assert response.status_code == 200
        assert response.json()["client_id"] == assigned_user.id
        assert response.json()["agent_id"] == agent.id
        assert response.json()["agency_id"] == agent.agency_id
        assert response.json()["bookingId"] == mock_amocrm_hook.return_value

        # проверка вызова замоканых функций/сервисов с сигнатурой
        mock_send_email.assert_called_once_with(
            recipients=[assigned_user.email],
            agent_name=payload["agency_contact"],
            unassign_link=mock_generate_unassign_link.return_value,
            slug="assign_client",
        )
        mock_notify_client_sms.assert_called_once_with(
            client_id=assigned_user.id,
            un_assignation_link=mock_generate_unassign_link.return_value,
            agent_name=payload["agency_contact"],
        )

    @patch("common.dependencies.users.DeletedUserCheck.__call__", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase._send_email", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase._notify_client_sms", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase.generate_unassign_link")
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase._create_task_instance")
    @patch("common.amocrm.components.notes.AmoCRMNotes.send_contact_note", new_callable=AsyncMock)
    @patch("common.amocrm.components.contacts.AmoCRMContacts.fetch_contact", new_callable=AsyncMock)
    @patch("common.amocrm.components.leads.AmoCRMLeads.create_lead", new_callable=AsyncMock)
    @patch("common.amocrm.components.leads.AmoCRMLeads.leads_unlink_entities", new_callable=AsyncMock)
    @patch("common.amocrm.components.leads.AmoCRMLeads.leads_link_entities", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__ainit__", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__aexit__", new_callable=AsyncMock)
    async def test_assign_client_amocrm_hook(
            self,
            mock_amocrm_aexit,
            mock_amocrm_ainit,
            mock_amocrm_leads_link_entities,
            mock_amocrm_leads_unlink_entities,
            mock_amocrm_create_lead,
            mock_amocrm_fetch_contact,
            mock_amocrm_send_contact_note,
            mock_create_task_instance,
            mock_generate_unassign_link,
            mock_notify_client_sms,
            mock_send_email,
            mock_delete_user_check,
            async_client,
            agent,
            agent_authorization,
            assigned_user,
            consultation_type,
            unique_status_partially_pinned,
            unique_user_check,
            project_for_assign,
            booking_fixing_conditions_matrix,
            amo_status_for_assign,
            booking_source_lk_booking_assign,
            booking_repo,
            faker,
    ):
        mock_amocrm_fetch_contact.return_value = AmoContact(
            id=assigned_user.amocrm_id,
            name=assigned_user.name + assigned_user.surname + assigned_user.patronymic,
            created_at=int(datetime.datetime.now(tz=UTC).timestamp()),
            updated_at=int(datetime.datetime.now(tz=UTC).timestamp()),
            _embedded=AmoContactEmbedded()
        )
        mock_amocrm_create_lead.return_value = [AmoLead(
            id=faker.random_int(min=111111111, max=999999999),
            created_at=int(datetime.datetime.now(tz=UTC).timestamp()),
            updated_at=int(datetime.datetime.now(tz=UTC).timestamp()),
        )]
        mock_generate_unassign_link.return_value = faker.url()
        mock_amocrm_send_contact_note.return_value = dict(
            route=faker.url(),
            status=200,
            request_data=faker.word(),
            data=faker.word(),
        )

        headers = {"Authorization": agent_authorization}
        payload = dict(
            name=assigned_user.name,
            phone=assigned_user.phone,
            user_id=assigned_user.id,
            check_id=unique_user_check.id,
            consultation_type=consultation_type.slug,
            active_projects=[project_for_assign.id],
        )
        response = await async_client.post("/users/agent/assign_client", headers=headers, json=payload)

        # получаем данные из тестовой БД для проверки
        booking = await booking_repo.retrieve(filters=dict(amocrm_id=mock_amocrm_create_lead.return_value[0].id))

        # общий ответ апи
        assert response.status_code == 200
        assert response.json()["client_id"] == assigned_user.id
        assert response.json()["agent_id"] == agent.id
        assert response.json()["agency_id"] == agent.agency_id
        assert response.json()["bookingId"] == booking.id

        # проверка параметров созданной сделки
        assert booking.user_id == assigned_user.id
        assert booking.agent_id == agent.id
        assert booking.project_id == project_for_assign.id
        assert booking.amocrm_stage == BookingStages.START
        assert booking.amocrm_substage == BookingSubstages.ASSIGN_AGENT
        assert booking.agency_id == agent.agency_id
        assert booking.amocrm_status_id == amo_status_for_assign.id
        assert booking.created_source == BookingCreatedSources.LK_ASSIGN
        assert booking.booking_source_id == booking_source_lk_booking_assign.id
        assert AssignClientCase.lk_broker_tag[0] in booking.tags
        assert booking.active is True

        # проверка вызова замоканых функций/сервисов с сигнатурой
        mock_create_task_instance.assert_called_once_with([booking.id], booking_created=True)
        mock_amocrm_fetch_contact.assert_called_once_with(
            user_id=assigned_user.amocrm_id,
            query_with=[AmoContactQueryWith.leads],
        )
        mock_amocrm_create_lead.assert_called_once()
        mock_amocrm_leads_link_entities.assert_called_once()
        mock_amocrm_leads_unlink_entities.assert_called_once()
        mock_amocrm_ainit.assert_called()
        mock_amocrm_aexit.assert_called()

    @patch("common.dependencies.users.DeletedUserCheck.__call__", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase._send_email", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase._notify_client_sms", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase.generate_unassign_link")
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase._create_task_instance")
    @patch("common.amocrm.components.notes.AmoCRMNotes.send_contact_note", new_callable=AsyncMock)
    @patch("common.amocrm.components.contacts.AmoCRMContacts.fetch_contact", new_callable=AsyncMock)
    @patch("common.amocrm.components.leads.AmoCRMLeads.create_lead", new_callable=AsyncMock)
    @patch("common.amocrm.components.leads.AmoCRMLeads.leads_unlink_entities", new_callable=AsyncMock)
    @patch("common.amocrm.components.leads.AmoCRMLeads.leads_link_entities", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__ainit__", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__aexit__", new_callable=AsyncMock)
    async def test_assign_client_by_repres_amocrm_hook(
            self,
            mock_amocrm_aexit,
            mock_amocrm_ainit,
            mock_amocrm_leads_link_entities,
            mock_amocrm_leads_unlink_entities,
            mock_amocrm_create_lead,
            mock_amocrm_fetch_contact,
            mock_amocrm_send_contact_note,
            mock_create_task_instance,
            mock_generate_unassign_link,
            mock_notify_client_sms,
            mock_send_email,
            mock_delete_user_check,
            async_client,
            repres_for_assign,
            repres_authorization_for_assign,
            assigned_user,
            consultation_type,
            unique_status_partially_pinned,
            unique_user_check,
            project_for_assign,
            booking_fixing_conditions_matrix,
            amo_status_for_assign,
            booking_source_lk_booking_assign,
            booking_repo,
            faker,
    ):
        mock_amocrm_fetch_contact.return_value = AmoContact(
            id=assigned_user.amocrm_id,
            name=assigned_user.name + assigned_user.surname + assigned_user.patronymic,
            created_at=int(datetime.datetime.now(tz=UTC).timestamp()),
            updated_at=int(datetime.datetime.now(tz=UTC).timestamp()),
            _embedded=AmoContactEmbedded()
        )
        mock_amocrm_create_lead.return_value = [AmoLead(
            id=faker.random_int(min=111111111, max=999999999),
            created_at=int(datetime.datetime.now(tz=UTC).timestamp()),
            updated_at=int(datetime.datetime.now(tz=UTC).timestamp()),
        )]
        mock_generate_unassign_link.return_value = faker.url()
        mock_amocrm_send_contact_note.return_value = dict(
            route=faker.url(),
            status=200,
            request_data=faker.word(),
            data=faker.word(),
        )

        headers = {"Authorization": repres_authorization_for_assign}
        payload = dict(
            name=assigned_user.name,
            phone=assigned_user.phone,
            user_id=assigned_user.id,
            check_id=unique_user_check.id,
            consultation_type=consultation_type.slug,
            active_projects=[project_for_assign.id],
        )
        response = await async_client.post("/users/repres/assign_client", headers=headers, json=payload)

        # получаем данные из тестовой БД для проверки
        booking = await booking_repo.retrieve(filters=dict(amocrm_id=mock_amocrm_create_lead.return_value[0].id))

        # общий ответ апи
        assert response.status_code == 200
        assert response.json()["client_id"] == assigned_user.id
        assert response.json()["agent_id"] == repres_for_assign.id
        assert response.json()["agency_id"] == repres_for_assign.agency_id
        assert response.json()["bookingId"] == booking.id

        # проверка параметров созданной сделки
        assert booking.user_id == assigned_user.id
        assert booking.agent_id == repres_for_assign.id
        assert booking.project_id == project_for_assign.id
        assert booking.amocrm_stage == BookingStages.START
        assert booking.amocrm_substage == BookingSubstages.ASSIGN_AGENT
        assert booking.agency_id == repres_for_assign.agency_id
        assert booking.amocrm_status_id == amo_status_for_assign.id
        assert booking.created_source == BookingCreatedSources.LK_ASSIGN
        assert booking.booking_source_id == booking_source_lk_booking_assign.id
        assert AssignClientCase.lk_broker_tag[0] in booking.tags
        assert booking.active is True

        # проверка вызова замоканых функций/сервисов с сигнатурой
        mock_create_task_instance.assert_called_once_with([booking.id], booking_created=True)
        mock_amocrm_fetch_contact.assert_called_once_with(
            user_id=assigned_user.amocrm_id,
            query_with=[AmoContactQueryWith.leads],
        )
        mock_amocrm_create_lead.assert_called_once()
        mock_amocrm_leads_link_entities.assert_called_once()
        mock_amocrm_leads_unlink_entities.assert_called_once()
        mock_amocrm_ainit.assert_called()
        mock_amocrm_aexit.assert_called()

    @patch("common.dependencies.users.DeletedUserCheck.__call__", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase._send_email", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase._notify_client_sms", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase.generate_unassign_link")
    @patch("common.amocrm.components.notes.AmoCRMNotes.send_contact_note", new_callable=AsyncMock)
    @patch("common.amocrm.components.contacts.AmoCRMContacts.fetch_contact", new_callable=AsyncMock)
    @patch("common.amocrm.components.leads.AmoCRMLeads.leads_unlink_entities", new_callable=AsyncMock)
    @patch("common.amocrm.components.leads.AmoCRMLeads.leads_link_entities", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__ainit__", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__aexit__", new_callable=AsyncMock)
    async def test_assign_client_amocrm_hook_with_existed_booking(
        self,
        mock_amocrm_aexit,
        mock_amocrm_ainit,
        mock_amocrm_leads_link_entities,
        mock_amocrm_leads_unlink_entities,
        mock_amocrm_fetch_contact,
        mock_amocrm_send_contact_note,
        mock_generate_unassign_link,
        mock_notify_client_sms,
        mock_send_email,
        mock_delete_user_check,
        async_client,
        agent,
        agent_authorization,
        assigned_user,
        consultation_type,
        unique_status_partially_pinned,
        unique_user_check,
        project_for_assign,
        booking_for_assign,
        faker,
    ):
        mock_amocrm_fetch_contact.return_value = AmoContact(
            id=assigned_user.amocrm_id,
            name=assigned_user.name + assigned_user.surname + assigned_user.patronymic,
            created_at=int(datetime.datetime.now(tz=UTC).timestamp()),
            updated_at=int(datetime.datetime.now(tz=UTC).timestamp()),
            _embedded=AmoContactEmbedded()
        )
        mock_generate_unassign_link.return_value = faker.url()
        mock_amocrm_send_contact_note.return_value = dict(
            route=faker.url(),
            status=200,
            request_data=faker.word(),
            data=faker.word(),
        )

        headers = {"Authorization": agent_authorization}
        payload = dict(
            name=assigned_user.name,
            phone=assigned_user.phone,
            user_id=assigned_user.id,
            check_id=unique_user_check.id,
            consultation_type=consultation_type.slug,
            active_projects=[project_for_assign.id],
        )
        response = await async_client.post("/users/agent/assign_client", headers=headers, json=payload)

        # общий ответ апи
        assert response.status_code == 200
        assert response.json()["client_id"] == assigned_user.id
        assert response.json()["agent_id"] == agent.id
        assert response.json()["agency_id"] == agent.agency_id
        assert response.json()["bookingId"] == booking_for_assign.id

        # проверка параметров созданной сделки
        assert booking_for_assign.user_id == assigned_user.id
        assert booking_for_assign.agent_id == agent.id
        assert booking_for_assign.project_id == project_for_assign.id
        assert booking_for_assign.amocrm_stage == BookingStages.START
        assert booking_for_assign.amocrm_substage == BookingSubstages.ASSIGN_AGENT
        assert booking_for_assign.active is True

        # проверка вызова замоканых функций/сервисов с сигнатурой
        mock_amocrm_fetch_contact.assert_called_once_with(
            user_id=assigned_user.amocrm_id,
            query_with=[AmoContactQueryWith.leads],
        )
        mock_amocrm_leads_link_entities.assert_called_once()
        mock_amocrm_leads_unlink_entities.assert_called_once()
        mock_amocrm_ainit.assert_called()
        mock_amocrm_aexit.assert_called()

    @patch("common.dependencies.users.DeletedUserCheck.__call__", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase._send_email", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase._amocrm_hook", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase._notify_client_sms", new_callable=AsyncMock)
    @patch("src.users.use_cases.agents_client_assign.AssignClientCase.generate_unassign_link")
    @patch("common.amocrm.components.notes.AmoCRMNotes.send_contact_note", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__ainit__", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__aexit__", new_callable=AsyncMock)
    async def test_assign_client(
        self,
        mock_amocrm_aexit,
        mock_amocrm_ainit,
        mock_amocrm_send_contact_note,
        mock_generate_unassign_link,
        mock_notify_client_sms,
        mock_amocrm_hook,
        mock_send_email,
        mock_delete_user_check,
        async_client,
        agent,
        agent_authorization,
        assigned_user_with_old_agent,
        consultation_type,
        unique_status_partially_pinned,
        user_pinning_status_repo,
        confirm_client_assign_repo,
        check_repo,
        unique_user_check,
        client_assign_maintenance_repo,
        faker,
    ):
        mock_generate_unassign_link.return_value = faker.url()
        mock_amocrm_hook.return_value = faker.random_int(min=1, max=99)
        mock_amocrm_send_contact_note.return_value = dict(
            route=faker.url(),
            status=200,
            request_data=faker.word(),
            data=faker.word(),
        )

        headers = {"Authorization": agent_authorization}
        payload = dict(
            name=assigned_user_with_old_agent.name,
            phone=assigned_user_with_old_agent.phone,
            user_id=assigned_user_with_old_agent.id,
            check_id=unique_user_check.id,
            consultation_type=consultation_type.slug,
            assignation_comment=faker.word(),
        )
        response = await async_client.post("/users/agent/assign_client", headers=headers, json=payload)

        # получаем данные из тестовой БД для проверки
        user_pinning_status = await user_pinning_status_repo.retrieve(
            filters=dict(
                user_id=assigned_user_with_old_agent.id,
                unique_status__slug=UserPinningStatusType.PARTIALLY_PINNED,
            ),
            related_fields=["unique_status"],
        )
        confirm_client_assign = await confirm_client_assign_repo.retrieve(
            filters=dict(
                client_id=assigned_user_with_old_agent.id,
                agent_id=agent.id,
            )
        )
        user_check = await check_repo.retrieve(filters=dict(id=unique_user_check.id))
        client_assign_maintenance = await client_assign_maintenance_repo.retrieve(
            filters=dict(client_phone=assigned_user_with_old_agent.phone, broker_amocrm_id=agent.amocrm_id),
        )

        # общий ответ апи
        assert response.status_code == 200
        assert response.json()["client_id"] == assigned_user_with_old_agent.id
        assert response.json()["agent_id"] == agent.id
        assert response.json()["agency_id"] == agent.agency_id
        assert response.json()["bookingId"] == mock_amocrm_hook.return_value
        # проверка создания статуса закрепления
        assert user_pinning_status.user_id == assigned_user_with_old_agent.id
        assert user_pinning_status.unique_status.slug == UserPinningStatusType.PARTIALLY_PINNED
        # проверка подтверждения закрепления клиента за агентом
        assert confirm_client_assign.agent_id == agent.id
        assert confirm_client_assign.client_id == assigned_user_with_old_agent.id
        # проверка обновленной проверки
        assert user_check.agent_id == agent.id
        assert user_check.user_id == assigned_user_with_old_agent.id
        # проверка создания модели подтверждения закрепления клиента за агентом
        assert client_assign_maintenance.client_phone == assigned_user_with_old_agent.phone
        assert client_assign_maintenance.broker_amocrm_id == agent.amocrm_id

        # проверка вызова замоканых функций/сервисов с сигнатурой
        mock_delete_user_check.assert_called_once()
        mock_generate_unassign_link.assert_called_once_with(
            agent_id=agent.id,
            client_id=assigned_user_with_old_agent.id,
        )
        mock_amocrm_hook.assert_called_once()
        mock_send_email.assert_has_calls(
            [
                call(
                    recipients=[assigned_user_with_old_agent.agent.email],
                    agent_name=assigned_user_with_old_agent.agent.full_name,
                    client_name=assigned_user_with_old_agent.full_name,
                    slug=AssignClientCase.previous_agent_email_slug,
                ),
                call(
                    recipients=[assigned_user_with_old_agent.email],
                    agent_name=agent.full_name,
                    unassign_link=mock_generate_unassign_link.return_value,
                    slug=AssignClientCase.mail_event_slug,
                )
            ],
            any_order=True,
        )
        mock_notify_client_sms.assert_called_once_with(
            client_id=assigned_user_with_old_agent.id,
            un_assignation_link=mock_generate_unassign_link.return_value,
            agent_name=agent.full_name,
        )
        mock_amocrm_send_contact_note.assert_called_once_with(
            contact_id=assigned_user_with_old_agent.amocrm_id,
            message=f"{consultation_type.name}: {payload['assignation_comment']}",
        )
        mock_amocrm_ainit.assert_called_once()
        mock_amocrm_aexit.assert_called_once()
