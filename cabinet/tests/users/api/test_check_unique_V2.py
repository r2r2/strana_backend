import pytest
import datetime
from typing import Any
from unittest.mock import AsyncMock, patch
from pytz import UTC

from common import amocrm
from common.amocrm.types.contact import AmoContact, AmoContactEmbedded
from common.amocrm.types.lead import AmoLead
from common.amocrm.types.common import AmoCustomField, AmoCustomFieldValue
from config import amocrm_config
from src.agents import repos as agents_repos
from src.projects import repos as projects_repos
from src.users import repos as users_repos
from src.users import services as user_services
from src.users import constants as user_constants

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


class TestCheckUniqueV2Service:
    async def test_check_unique_v2_service_assertion_error(
        self,
        user_for_checking,
        user_for_checking_without_phone,
        user_check_without_status,
        faker,
    ):
        resources: dict[str, Any] = dict(
            amocrm_class=amocrm.AmoCRM,
            user_repo=users_repos.UserRepo,
            check_repo=users_repos.CheckRepo,
            history_check_repo=users_repos.CheckHistoryRepo,
            amocrm_history_check_log_repo=users_repos.AmoCrmCheckLogRepo,
            agent_repo=agents_repos.AgentRepo,
            check_term_repo=users_repos.CheckTermRepo,
            project_repo=projects_repos.ProjectRepo,
            amocrm_config=amocrm_config,
        )
        check_unique_service: user_services.CheckUniqueServiceV2 = user_services.CheckUniqueServiceV2(**resources)

        try:
            await check_unique_service(user=user_for_checking)
        except AssertionError as assertion_error:
            assert str(assertion_error) == "Не найден телефон или проверка (Check)"

        try:
            await check_unique_service(user=user_for_checking_without_phone, check=user_check_without_status)
        except AssertionError as assertion_error:
            assert str(assertion_error) == "Не найден телефон или проверка (Check)"

    async def test_check_unique_v2_service_unique_status_error(
        self,
        user_for_checking,
        user_check_without_status,
        agent_with_user_phone,
        unique_status_error,
        faker,
    ):
        resources: dict[str, Any] = dict(
            amocrm_class=amocrm.AmoCRM,
            user_repo=users_repos.UserRepo,
            check_repo=users_repos.CheckRepo,
            history_check_repo=users_repos.CheckHistoryRepo,
            amocrm_history_check_log_repo=users_repos.AmoCrmCheckLogRepo,
            agent_repo=agents_repos.AgentRepo,
            check_term_repo=users_repos.CheckTermRepo,
            project_repo=projects_repos.ProjectRepo,
            amocrm_config=amocrm_config,
        )
        check_unique_service: user_services.CheckUniqueServiceV2 = user_services.CheckUniqueServiceV2(**resources)
        bool_result, history_check_logs_ids = await check_unique_service(
            check=user_check_without_status,
            user=user_for_checking,
        )
        unique_status = await user_check_without_status.unique_status

        assert bool_result is False
        assert len(history_check_logs_ids) == 0
        assert unique_status.slug == user_constants.UserStatus.ERROR

    @patch("common.amocrm.components.contacts.AmoCRMContacts._parse_contacts_data_v4")
    @patch("common.amocrm.amocrm.AmoCRM._request_get_v4", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__aexit__", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__ainit__", new_callable=AsyncMock)
    async def test_check_unique_v2_service_has_no_contact_in_amo(
        self,
        mock_amocrm_ainit,
        mock_amocrm_aexit,
        mock_amocrm_request_get_v4,
        mock_amocrm_parse_contacts_data_v4,
        user_for_checking,
        agent,
        user_check_without_status,
        unique_status_unique,
        faker,
    ):
        mock_amocrm_parse_contacts_data_v4.return_value = []

        resources: dict[str, Any] = dict(
            amocrm_class=amocrm.AmoCRM,
            user_repo=users_repos.UserRepo,
            check_repo=users_repos.CheckRepo,
            history_check_repo=users_repos.CheckHistoryRepo,
            amocrm_history_check_log_repo=users_repos.AmoCrmCheckLogRepo,
            agent_repo=agents_repos.AgentRepo,
            check_term_repo=users_repos.CheckTermRepo,
            project_repo=projects_repos.ProjectRepo,
            amocrm_config=amocrm_config,
        )
        check_unique_service: user_services.CheckUniqueServiceV2 = user_services.CheckUniqueServiceV2(**resources)
        bool_result, history_check_logs_ids = await check_unique_service(
            check=user_check_without_status,
            user=user_for_checking,
            agent_id=agent.id,
        )
        unique_status = await user_check_without_status.unique_status

        assert bool_result is True
        assert len(history_check_logs_ids) == 1
        assert unique_status.slug == user_constants.UserStatus.UNIQUE

        mock_amocrm_ainit.assert_called_once()
        mock_amocrm_aexit.assert_called_once()
        mock_amocrm_parse_contacts_data_v4.assert_called_once()
        mock_amocrm_request_get_v4.assert_called_once_with(
            route="/contacts",
            query={'query': user_for_checking.phone[-10:], 'with': 'leads'},
        )

    @patch("common.amocrm.components.leads.AmoCRMLeads.fetch_leads")
    @patch("common.amocrm.components.contacts.AmoCRMContacts._parse_contacts_data_v4")
    @patch("common.amocrm.amocrm.AmoCRM._request_get_v4", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__aexit__", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__ainit__", new_callable=AsyncMock)
    async def test_check_unique_v2_service_has_contact_in_amo_with_terms_1(
        self,
        mock_amocrm_ainit,
        mock_amocrm_aexit,
        mock_amocrm_request_get_v4,
        mock_amocrm_parse_contacts_data_v4,
        mock_amocrm_fetch_leads,
        user_for_checking,
        agent,
        user_check_without_status,
        project_for_assign,
        amo_pipeline_for_assign,
        amo_status_for_assign,
        unique_status_unique,
        city,
        check_term_1,
        faker,
    ):
        mock_amocrm_parse_contacts_data_v4.return_value = [AmoContact(
            id=user_for_checking.amocrm_id,
            name=user_for_checking.name + user_for_checking.surname + user_for_checking.patronymic,
            created_at=int(datetime.datetime.now(tz=UTC).timestamp()),
            updated_at=int(datetime.datetime.now(tz=UTC).timestamp()),
            _embedded=AmoContactEmbedded(
                leads=[AmoLead(
                    id=faker.random_int(min=111111111, max=999999999),
                    created_at=int(datetime.datetime.now(tz=UTC).timestamp()),
                    updated_at=int(datetime.datetime.now(tz=UTC).timestamp()),
                )]
            ),
        )]
        mock_amocrm_fetch_leads.return_value = [AmoLead(
            id=faker.random_int(min=111111111, max=999999999),
            created_at=int(datetime.datetime.now(tz=UTC).timestamp()),
            updated_at=int(datetime.datetime.now(tz=UTC).timestamp()),
            pipeline_id=amo_pipeline_for_assign.id,
            status_id=amo_status_for_assign.id,
            custom_fields_values=[
                AmoCustomField(
                    field_id=amocrm.AmoCRM.project_field_id,
                    values=[AmoCustomFieldValue(value=project_for_assign.amocrm_name)],
                ),
                AmoCustomField(
                    field_id=amocrm.AmoCRM.city_field_id,
                    values=[AmoCustomFieldValue(value=city.name)],
                ),
            ]
        )]

        resources: dict[str, Any] = dict(
            amocrm_class=amocrm.AmoCRM,
            user_repo=users_repos.UserRepo,
            check_repo=users_repos.CheckRepo,
            history_check_repo=users_repos.CheckHistoryRepo,
            amocrm_history_check_log_repo=users_repos.AmoCrmCheckLogRepo,
            agent_repo=agents_repos.AgentRepo,
            check_term_repo=users_repos.CheckTermRepo,
            project_repo=projects_repos.ProjectRepo,
            amocrm_config=amocrm_config,
        )
        check_unique_service: user_services.CheckUniqueServiceV2 = user_services.CheckUniqueServiceV2(**resources)
        bool_result, history_check_logs_ids = await check_unique_service(
            check=user_check_without_status,
            user=user_for_checking,
            agent_id=agent.id,
        )
        unique_status = await user_check_without_status.unique_status

        assert bool_result is True
        assert len(history_check_logs_ids) == 1
        assert unique_status.slug == user_constants.UserPinningStatusType.PARTIALLY_PINNED
        assert user_check_without_status.amocrm_id == mock_amocrm_fetch_leads.return_value[0].id

        mock_amocrm_ainit.assert_called_once()
        mock_amocrm_aexit.assert_called_once()
        mock_amocrm_fetch_leads.assert_called_once()
        mock_amocrm_parse_contacts_data_v4.assert_called_once()
        mock_amocrm_request_get_v4.assert_called_once_with(
            route="/contacts",
            query={'query': user_for_checking.phone[-10:], 'with': 'leads'},
        )

    @patch("src.users.services.check_unique_v2.CheckUniqueServiceV2._check_lead_has_agent", new_callable=AsyncMock)
    @patch("common.amocrm.components.leads.AmoCRMLeads.fetch_leads")
    @patch("common.amocrm.components.contacts.AmoCRMContacts._parse_contacts_data_v4")
    @patch("common.amocrm.amocrm.AmoCRM._request_get_v4", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__aexit__", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__ainit__", new_callable=AsyncMock)
    async def test_check_unique_v2_service_has_contact_in_amo_with_terms_2(
        self,
        mock_amocrm_ainit,
        mock_amocrm_aexit,
        mock_amocrm_request_get_v4,
        mock_amocrm_parse_contacts_data_v4,
        mock_amocrm_fetch_leads,
        mock_check_lead_has_agent,
        user_for_checking_with_agent,
        agent,
        user_check_without_status,
        project_for_assign,
        amo_pipeline_for_assign,
        amo_status_for_assign,
        unique_status_unique,
        city,
        check_term_2,
        faker,
    ):
        mock_check_lead_has_agent.return_value = True
        mock_amocrm_parse_contacts_data_v4.return_value = [AmoContact(
            id=user_for_checking_with_agent.amocrm_id,
            name=(
                user_for_checking_with_agent.name
                + user_for_checking_with_agent.surname
                + user_for_checking_with_agent.patronymic
            ),
            created_at=int(datetime.datetime.now(tz=UTC).timestamp()),
            updated_at=int(datetime.datetime.now(tz=UTC).timestamp()),
            _embedded=AmoContactEmbedded(
                leads=[AmoLead(
                    id=faker.random_int(min=111111111, max=999999999),
                    created_at=int(datetime.datetime.now(tz=UTC).timestamp()),
                    updated_at=int(datetime.datetime.now(tz=UTC).timestamp()),
                )]
            ),
        )]
        mock_amocrm_fetch_leads.return_value = [AmoLead(
            id=faker.random_int(min=111111111, max=999999999),
            created_at=int(datetime.datetime.now(tz=UTC).timestamp()),
            updated_at=int(datetime.datetime.now(tz=UTC).timestamp()),
            pipeline_id=amo_pipeline_for_assign.id,
            status_id=amo_status_for_assign.id,
            custom_fields_values=[
                AmoCustomField(
                    field_id=amocrm.AmoCRM.project_field_id,
                    values=[AmoCustomFieldValue(value=project_for_assign.amocrm_name)],
                ),
                AmoCustomField(
                    field_id=amocrm.AmoCRM.city_field_id,
                    values=[AmoCustomFieldValue(value=city.name)],
                ),
            ]
        )]

        resources: dict[str, Any] = dict(
            amocrm_class=amocrm.AmoCRM,
            user_repo=users_repos.UserRepo,
            check_repo=users_repos.CheckRepo,
            history_check_repo=users_repos.CheckHistoryRepo,
            amocrm_history_check_log_repo=users_repos.AmoCrmCheckLogRepo,
            agent_repo=agents_repos.AgentRepo,
            check_term_repo=users_repos.CheckTermRepo,
            project_repo=projects_repos.ProjectRepo,
            amocrm_config=amocrm_config,
        )
        check_unique_service: user_services.CheckUniqueServiceV2 = user_services.CheckUniqueServiceV2(**resources)
        bool_result, history_check_logs_ids = await check_unique_service(
            check=user_check_without_status,
            user=user_for_checking_with_agent,
            agent_id=agent.id,
        )
        unique_status = await user_check_without_status.unique_status

        assert bool_result is True
        assert len(history_check_logs_ids) == 1
        assert unique_status.slug == user_constants.UserPinningStatusType.PINNED
        assert user_check_without_status.amocrm_id == mock_amocrm_fetch_leads.return_value[0].id

        mock_amocrm_ainit.assert_called_once()
        mock_amocrm_aexit.assert_called_once()
        mock_amocrm_fetch_leads.assert_called_once()
        mock_amocrm_parse_contacts_data_v4.assert_called_once()
        mock_amocrm_request_get_v4.assert_called_once_with(
            route="/contacts",
            query={'query': user_for_checking_with_agent.phone[-10:], 'with': 'leads'},
        )
        mock_check_lead_has_agent.assert_called_once()

    @patch("src.users.services.check_unique_v2.CheckUniqueServiceV2._check_lead_has_agent", new_callable=AsyncMock)
    @patch("common.amocrm.components.leads.AmoCRMLeads.fetch_leads")
    @patch("common.amocrm.components.contacts.AmoCRMContacts._parse_contacts_data_v4")
    @patch("common.amocrm.amocrm.AmoCRM._request_get_v4", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__aexit__", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__ainit__", new_callable=AsyncMock)
    async def test_check_unique_v2_service_has_contact_in_amo_with_terms_3(
        self,
        mock_amocrm_ainit,
        mock_amocrm_aexit,
        mock_amocrm_request_get_v4,
        mock_amocrm_parse_contacts_data_v4,
        mock_amocrm_fetch_leads,
        mock_check_lead_has_agent,
        user_for_checking_with_agent_agency,
        agent,
        user_check_without_status,
        project_for_assign,
        amo_pipeline_for_assign,
        amo_status_for_assign,
        unique_status_unique,
        city,
        check_term_3,
        faker,
    ):
        mock_check_lead_has_agent.return_value = True
        mock_amocrm_parse_contacts_data_v4.return_value = [AmoContact(
            id=user_for_checking_with_agent_agency.amocrm_id,
            name=(
                user_for_checking_with_agent_agency.name
                + user_for_checking_with_agent_agency.surname
                + user_for_checking_with_agent_agency.patronymic
            ),
            created_at=int(datetime.datetime.now(tz=UTC).timestamp()),
            updated_at=int(datetime.datetime.now(tz=UTC).timestamp()),
            _embedded=AmoContactEmbedded(
                leads=[AmoLead(
                    id=faker.random_int(min=111111111, max=999999999),
                    created_at=int(datetime.datetime.now(tz=UTC).timestamp()),
                    updated_at=int(datetime.datetime.now(tz=UTC).timestamp()),
                )]
            ),
        )]
        mock_amocrm_fetch_leads.return_value = [AmoLead(
            id=faker.random_int(min=111111111, max=999999999),
            created_at=int(datetime.datetime.now(tz=UTC).timestamp()),
            updated_at=int(datetime.datetime.now(tz=UTC).timestamp()),
            pipeline_id=amo_pipeline_for_assign.id,
            status_id=amo_status_for_assign.id,
            custom_fields_values=[
                AmoCustomField(
                    field_id=amocrm.AmoCRM.project_field_id,
                    values=[AmoCustomFieldValue(value=project_for_assign.amocrm_name)],
                ),
                AmoCustomField(
                    field_id=amocrm.AmoCRM.city_field_id,
                    values=[AmoCustomFieldValue(value=city.name)],
                ),
            ]
        )]

        resources: dict[str, Any] = dict(
            amocrm_class=amocrm.AmoCRM,
            user_repo=users_repos.UserRepo,
            check_repo=users_repos.CheckRepo,
            history_check_repo=users_repos.CheckHistoryRepo,
            amocrm_history_check_log_repo=users_repos.AmoCrmCheckLogRepo,
            agent_repo=agents_repos.AgentRepo,
            check_term_repo=users_repos.CheckTermRepo,
            project_repo=projects_repos.ProjectRepo,
            amocrm_config=amocrm_config,
        )
        check_unique_service: user_services.CheckUniqueServiceV2 = user_services.CheckUniqueServiceV2(**resources)
        bool_result, history_check_logs_ids = await check_unique_service(
            check=user_check_without_status,
            user=user_for_checking_with_agent_agency,
            agent_id=agent.id,
        )
        unique_status = await user_check_without_status.unique_status

        assert bool_result is True
        assert len(history_check_logs_ids) == 1
        assert unique_status.slug == user_constants.UserPinningStatusType.PARTIALLY_PINNED
        assert user_check_without_status.amocrm_id == mock_amocrm_fetch_leads.return_value[0].id

        mock_amocrm_ainit.assert_called_once()
        mock_amocrm_aexit.assert_called_once()
        mock_amocrm_fetch_leads.assert_called_once()
        mock_amocrm_parse_contacts_data_v4.assert_called_once()
        mock_amocrm_request_get_v4.assert_called_once_with(
            route="/contacts",
            query={'query': user_for_checking_with_agent_agency.phone[-10:], 'with': 'leads'},
        )
        mock_check_lead_has_agent.assert_called()
