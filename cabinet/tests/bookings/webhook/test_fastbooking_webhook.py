import warnings
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from mock import AsyncMock
from pytz import UTC
from tortoise import Tortoise

from common import (
    amocrm,
    email,
    messages,
    requests,
    security,
    utils,
)
from common.amocrm import repos as amocrm_repos
from common.amocrm.types import AmoLead, AmoLeadEmbedded, AmoTag
from common.amocrm.types.lead import AmoLeadContact
from config import (
    amocrm_config,
    backend_config,
    site_config,
    tortoise_config,
)
from src.agents.repos import AgentRepo
from src.amocrm import repos as src_amocrm_repos
from src.amocrm.repos import AmocrmStatusRepo, AmocrmStatus
from src.booking import repos as booking_repos
from src.booking import services as booking_services
from src.booking import tasks, use_cases
from src.booking.constants import BookingCreatedSources, BookingStagesMapping, PaymentStatuses
from src.booking.exceptions import BookingRequestValidationError
from src.booking.repos import BookingSource, Booking
from src.booking.tasks import create_booking_log_task
from src.booking.types import CustomFieldValue
from src.buildings import repos as buildings_repos
from src.buildings.repos import Building
from src.floors import repos as floors_repos
from src.notifications import repos as notifications_repos
from src.notifications import services as notification_services
from src.projects import repos as projects_repos
from src.properties import repos as properties_repos
from src.properties import services as property_services
from src.properties.constants import PremiseType
from src.properties.repos import Property
from src.properties.services import (
    ImportPropertyServiceFactory,
)
from src.task_management.factories import CreateTaskInstanceServiceFactory
from src.task_management.tasks import update_task_instance_status_task
from src.users import constants as users_constants
from src.users import repos as users_repos
from src.users import services as users_services
from src.users.repos import User


pytestmark = pytest.mark.asyncio


class TestFastBookingWebhook:
    """
    Тест вебхука создания быстрой брони
    """

    lead_id: int = 111
    pipeline_id: int = 222
    status_id: int = 21197641  # "Бронь"
    user_amocrm_id: int = 444
    amocrm_class: type[amocrm.AmoCRM] = amocrm.AmoCRM
    property_type_map: tuple[str, str] = ("Квартира", "FLAT")
    site_host: str = site_config["site_host"]

    def setup(self):
        get_sms_template_service = notification_services.GetSmsTemplateService(
            sms_template_repo=notifications_repos.SmsTemplateRepo,
        )

        get_email_template_service = notification_services.GetEmailTemplateService(
            email_template_repo=notifications_repos.EmailTemplateRepo,
        )

        import_property_service: property_services.ImportPropertyService = (
            ImportPropertyServiceFactory.create()
        )
        resources: dict[str, Any] = dict(
            orm_class=Tortoise,
            orm_config=tortoise_config,
            amocrm_class=amocrm.AmoCRM,
            backend_config=backend_config,
            user_repo=users_repos.UserRepo,
            agent_repo=AgentRepo,
            floor_repo=floors_repos.FloorRepo,
            user_types=users_constants.UserType,
            global_id_encoder=utils.to_global_id,
            request_class=requests.GraphQLRequest,
            booking_repo=booking_repos.BookingRepo,
            project_repo=projects_repos.ProjectRepo,
            building_repo=buildings_repos.BuildingRepo,
            property_repo=properties_repos.PropertyRepo,
            create_booking_log_task=create_booking_log_task,
            import_property_service=import_property_service,
            statuses_repo=amocrm_repos.AmoStatusesRepo,
            amocrm_config=amocrm_config,
            check_booking_task=tasks.check_booking_task,
            amocrm_status_repo=src_amocrm_repos.AmocrmStatusRepo,
            update_task_instance_status_task=update_task_instance_status_task,
        )
        import_bookings_service: booking_services.ImportBookingsService = (
            booking_services.ImportBookingsService(**resources)
        )
        resources: dict[str, Any] = dict(
            amocrm_class=amocrm.AmoCRM,
            user_repo=users_repos.UserRepo,
            user_role_repo=users_repos.UserRoleRepo,
            import_bookings_service=import_bookings_service,
            amocrm_config=amocrm_config,
        )
        create_amocrm_contact_service: users_services.CreateContactService = (
            users_services.CreateContactService(**resources)
        )

        create_task_instance_service = CreateTaskInstanceServiceFactory.create()

        resources: dict[str, Any] = dict(
            backend_config=backend_config,
            check_booking_task=tasks.check_booking_task,
            sms_class=messages.SmsService,
            email_class=email.EmailService,
            user_repo=users_repos.UserRepo,
            booking_repo=booking_repos.BookingRepo,
            property_repo=properties_repos.PropertyRepo,
            building_booking_type_repo=buildings_repos.BuildingBookingTypeRepo(),
            amocrm_class=amocrm.AmoCRM,
            sql_request_class=requests.UpdateSqlRequest,
            token_creator=security.create_access_token,
            import_property_service=import_property_service,
            site_config=site_config,
            create_amocrm_contact_service=create_amocrm_contact_service,
            create_booking_log_task=create_booking_log_task,
            global_id_encoder=utils.to_global_id,
            global_id_decoder=utils.from_global_id,
            get_sms_template_service=get_sms_template_service,
            get_email_template_service=get_email_template_service,
            statuses_repo=src_amocrm_repos.AmocrmStatusRepo,
            create_task_instance_service=create_task_instance_service,
        )

        fast_booking_webhook_case: use_cases.FastBookingWebhookCase = (
            use_cases.FastBookingWebhookCase(**resources)
        )
        return fast_booking_webhook_case

    def _get_lead(self) -> AmoLead:
        lead_tags: list[str] = ["tag1", "tag2"]
        tags: list[AmoTag] = [AmoTag(name=tag) for tag in lead_tags]
        contacts: list[AmoLeadContact] = [
            AmoLeadContact(id=self.user_amocrm_id, is_main=True),
            AmoLeadContact(id=1, is_main=False),
        ]
        lead: AmoLead = AmoLead(
            id=self.lead_id,
            pipeline_id=self.pipeline_id,
            status_id=self.status_id,
            _embedded=AmoLeadEmbedded(
                tags=tags,
                contacts=contacts,
            ),
        )
        return lead

    def _get_lead_custom_fields(self) -> dict[int, CustomFieldValue]:
        lead_custom_fields: dict[int, CustomFieldValue] = {
            self.amocrm_class.property_str_type_field_id: CustomFieldValue(
                value=self.property_type_map[0],
            ),
            self.amocrm_class.property_field_id: CustomFieldValue(
                value="test",
                enum=123,
            ),
            self.amocrm_class.city_field_id: CustomFieldValue(
                value="Тюмень",
            ),
            self.amocrm_class.booking_type_field_id: CustomFieldValue(
                value="10 тыс - 20 дней",
                enum=999,
            ),
            self.amocrm_class.property_final_price_field_id: CustomFieldValue(
                value=10_000,
            ),
            self.amocrm_class.property_price_with_sale_field_id: CustomFieldValue(
                value=1000,
            ),
        }
        return lead_custom_fields

    @patch("common.amocrm.amocrm.AmoCRM.__ainit__", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__aexit__", new_callable=AsyncMock)
    async def test__call__(self, *_):
        """Happy path"""
        webhook: use_cases.FastBookingWebhookCase = self.setup()

        # Mocks ###########################################
        webhook._validate_lead = MagicMock()
        webhook._send_fast_booking_notify = AsyncMock()

        lead: AmoLead = self._get_lead()
        webhook._get_lead = AsyncMock(return_value=lead)

        lead_custom_fields: dict[int, CustomFieldValue] = self._get_lead_custom_fields()
        webhook._get_lead_custom_fields = MagicMock(return_value=lead_custom_fields)

        # Build Property ##########################################
        fake_property = {"id": 1}
        webhook._create_property = AsyncMock(return_value=fake_property)

        # Build user ##############################################
        user = {"id": 1}
        webhook._update_or_create_user_from_amo = AsyncMock(return_value=user)

        # Build fast_booking ######################################
        fake_fast_booking = {"id": 1}
        webhook._create_new_booking_from_amo = AsyncMock(return_value=fake_fast_booking)

        # Execute test function ###########################################
        test_data: dict[str, Any] = dict(
            amocrm_id=self.lead_id,
        )
        with warnings.catch_warnings():
            # Suppress warning RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
            warnings.simplefilter("ignore")
            await webhook(**test_data)

        # Asserts ###########################################
        webhook._get_lead.assert_awaited_once_with(
            amocrm_id=self.lead_id,
        )
        webhook._get_lead_custom_fields.assert_called_once_with(
            lead=lead,
        )
        webhook._validate_lead.assert_called_once_with(
            lead_custom_fields=lead_custom_fields,
        )
        webhook._create_property.assert_awaited_once_with(
            property_id=lead_custom_fields[self.amocrm_class.property_field_id].value,
            property_type=self.property_type_map[1],
        )
        webhook._update_or_create_user_from_amo.assert_awaited_once_with(
            main_contact_id=self.user_amocrm_id,
        )
        webhook._create_new_booking_from_amo.assert_awaited_once_with(
            lead=lead,
            lead_custom_fields=lead_custom_fields,
            user=user,
            booking_property=fake_property,
            booking_type_id=lead_custom_fields[self.amocrm_class.booking_type_field_id].enum,
        )
        webhook._send_fast_booking_notify.assert_awaited_once_with(
            user=user,
            booking=fake_fast_booking,
        )

    async def test_validate_lead(self):
        webhook: use_cases.FastBookingWebhookCase = self.setup()

        with pytest.raises(BookingRequestValidationError):
            webhook._validate_lead(lead_custom_fields={})

    @patch("src.properties.repos.PropertyRepo.retrieve", new_callable=AsyncMock)
    @patch("src.properties.repos.PropertyRepo.update_or_create", new_callable=AsyncMock)
    @pytest.mark.parametrize(
        "property_id, property_type_, global_id",
        [
            ("111", "FLAT", "R2xvYmFsRmxhdFR5cGU6MTEx"),
            ("222", "PARKING", "R2xvYmFsUGFya2luZ1NwYWNlVHlwZToyMjI="),
        ]
    )
    async def test_create_property(
        self,
        property_update_or_create,
        property_retrieve,
        property_id,
        property_type_,
        global_id,
    ):
        webhook: use_cases.FastBookingWebhookCase = self.setup()
        webhook._import_property = AsyncMock()

        booking_property = Property()
        booking_property.id = 1111

        property_update_or_create.return_value = booking_property
        property_retrieve.return_value = booking_property

        # Execute test function #############################
        result = await webhook._create_property(
            property_id=property_id,
            property_type=property_type_,
        )

        # Asserts ###########################################
        webhook._import_property.assert_awaited_once_with(
            property_=booking_property,
        )

        if property_type_ != "FLAT":
            property_data = dict(premise=PremiseType.NONRESIDENTIAL, type=property_type_)
        else:
            property_data = dict(premise=PremiseType.RESIDENTIAL, type=property_type_)

        property_update_or_create.assert_awaited_once_with(
            filters=dict(global_id=global_id),
            data=property_data,
        )
        property_retrieve.assert_called_once_with(
            filters=dict(id=booking_property.id),
            related_fields=["building", "project"],
        )
        assert result == booking_property

    @pytest.mark.parametrize("user_found", [True, False])
    async def test_update_or_create_user_from_amo(self, user_found):
        webhook: use_cases.FastBookingWebhookCase = self.setup()
        webhook.log_amocrm_user = MagicMock()

        if user_found:
            fake_updated_user = {"id": 1}
            fake_created_user = None
        else:
            fake_updated_user = None
            fake_created_user = {"id": 1}

        webhook.update_user = AsyncMock(return_value=fake_updated_user)
        webhook.create_user = AsyncMock(return_value=fake_created_user)

        amo_user_data: dict[str, Any] = dict(
            id=self.user_amocrm_id,
            phone="89991234455",
            email="email@email.com",
        )
        webhook.get_amocrm_user_data = AsyncMock(return_value=amo_user_data)

        # Execute test function #############################
        result = await webhook._update_or_create_user_from_amo(main_contact_id=self.user_amocrm_id)

        # Asserts ###########################################
        webhook.get_amocrm_user_data.assert_awaited_once_with(
            main_contact_id=self.user_amocrm_id,
        )
        webhook.update_user.assert_awaited_once_with(amo_user_data, self.user_amocrm_id)

        if user_found:
            webhook.create_user.assert_not_awaited()
            webhook.log_amocrm_user.assert_called_once_with(self.user_amocrm_id, fake_updated_user)
            assert result == fake_updated_user
            assert fake_created_user is None
        else:
            webhook.create_user.assert_awaited_once_with(amo_user_data, self.user_amocrm_id)
            webhook.log_amocrm_user.assert_called_once_with(self.user_amocrm_id, fake_created_user)
            assert result == fake_created_user
            assert fake_updated_user is None

    @patch("src.properties.repos.property.PropertyRepo.update", new_callable=AsyncMock)
    @patch("src.amocrm.repos.statuses.AmocrmStatusRepo.retrieve", new_callable=AsyncMock)
    @patch("src.booking.use_cases.fast_booking_webhook.get_booking_reserv_time", new_callable=AsyncMock)
    @patch("src.booking.use_cases.fast_booking_webhook.get_booking_source", new_callable=AsyncMock)
    async def test_create_new_booking_from_amo(
        self,
        _get_booking_source,
        _get_booking_reserv_time,
        amocrm_status_repo_retrieve,
        property_repo_update,
    ):
        b_source_slug: str = BookingCreatedSources.FAST_BOOKING

        webhook: use_cases.FastBookingWebhookCase = self.setup()

        # Mocks ###########################################
        webhook.create_task_instance = AsyncMock()
        webhook._property_backend_booking = AsyncMock(return_value="test")
        webhook.check_booking_task.apply_async = MagicMock()

        selected_booking_type = buildings_repos.BuildingBookingType()
        selected_booking_type.period = 7
        selected_booking_type.price = 50_000
        building_booking_type_repo = buildings_repos.BuildingBookingTypeRepo
        building_booking_type_repo.retrieve = AsyncMock(return_value=selected_booking_type)

        amocrm_status: AmocrmStatus = AmocrmStatus()
        amocrm_status_repo_retrieve.return_value = amocrm_status

        booking_source: BookingSource = BookingSource()
        booking_source.id = 1111
        booking_source.slug = b_source_slug

        _get_booking_source.return_value = booking_source
        _get_booking_reserv_time.return_value = 50.0

        property_repo_update.return_value = Property()

        lead: AmoLead = self._get_lead()
        lead_custom_fields: dict[int, CustomFieldValue] = self._get_lead_custom_fields()
        user: User = User()
        user.id = 1111

        building: Building = Building()
        building.id = 2222
        building.default_commission = 5.0

        booking_property: Property = Property()
        booking_property.id = 2222
        booking_property.building = building
        booking_property.floor_id = 2222
        booking_property.project_id = 2222
        booking_property.building_id = 2222

        booking_type_id: int = lead_custom_fields[self.amocrm_class.booking_type_field_id].enum
        expires = datetime.now(tz=UTC) + timedelta(hours=_get_booking_reserv_time.return_value)
        amocrm_substage: str = self.amocrm_class.get_lead_substage(lead.status_id)
        amocrm_stage: str = BookingStagesMapping()[amocrm_substage]
        booking_data = dict(
            floor_id=booking_property.floor_id,
            project_id=booking_property.project_id,
            building_id=booking_property.building_id,
            payment_amount=selected_booking_type.price,
            booking_period=selected_booking_type.period,
            start_commission=building.default_commission,
            commission=building.default_commission,
            until=datetime.now(tz=UTC) + timedelta(days=selected_booking_type.period),
            personal_filled=True,
            amocrm_id=lead.id,
            property=booking_property,
            user_id=user.id,
            origin=f"https://{self.site_host}",
            amocrm_stage=amocrm_stage,
            amocrm_substage=amocrm_substage,
            amocrm_status=amocrm_status,
            expires=expires,
            should_be_deactivated_by_timer=True,
            profitbase_booked=True,
            created_source=b_source_slug,  # todo: deprecated
            booking_source=booking_source,
            active=True,
            payment_status=PaymentStatuses.CREATED,
            tags=lead.embedded.tags,
        )
        booking: Booking = Booking()
        booking.id = 4444
        [setattr(booking, field_name, value) for field_name, value in booking_data.items()]

        webhook._booking_create = AsyncMock(return_value=booking)

        test_data: dict[str, Any] = dict(
            lead=lead,
            lead_custom_fields=lead_custom_fields,
            user=user,
            booking_property=booking_property,
            booking_type_id=booking_type_id,
        )
        # Execute test function #############################
        result = await webhook._create_new_booking_from_amo(**test_data)

        # Asserts ###########################################
        building_booking_type_repo.retrieve.assert_awaited_once_with(
            filters=dict(amocrm_id=booking_type_id),
        )
        amocrm_status_repo_retrieve.assert_awaited_once_with(
            filters=dict(id=lead.status_id),
        )
        _get_booking_source.assert_awaited_once_with(slug=b_source_slug)
        _get_booking_reserv_time.assert_awaited_once_with(
            created_source=booking_source.slug,
            booking_property=booking_property,
        )
        webhook._booking_create.assert_awaited_once()
        property_repo_update.assert_awaited_once_with(
            model=booking_property,
            data=dict(final_price=lead_custom_fields[self.amocrm_class.property_price_with_sale_field_id].value),
        )

        assert result == booking
