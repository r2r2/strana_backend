from asyncio import Task
from datetime import datetime, timedelta
from typing import Any, Callable, Optional, Type, Union, Tuple

import structlog
from common.amocrm import AmoCRM
from common.amocrm.constants import AmoLeadQueryWith
from common.amocrm.types import AmoContact, AmoLead
from pytz import UTC
from src.buildings import repos as buildings_repos
from src.buildings.repos.building import Building, BuildingBookingType
from src.properties.constants import PremiseType, PropertyTypes
from src.properties.repos import Property
from src.users.constants import UserType
from src.users.repos.user import User, UserRepo

from ...users.services import CreateContactService
from ..constants import BookingCreatedSources
from ..entities import BaseBookingCase
from ..exceptions import BookingRequestValidationError
from ..maintenance.amocrm_leed_note import amocrm_note
from ..mixins import BookingLogMixin
from ..repos import Booking, BookingRepo
from ..types import (BookingAmoCRM, BookingEmail, BookingPropertyRepo,
                     BookingSms, BookingSqlUpdateRequest,
                     BookingTypeNamedTuple, CustomFieldValue, WebhookLead)


class FastBookingWebhookCase(BaseBookingCase, BookingLogMixin):
    """
    Обработка быстрой брони по вебхуку
    """

    sms_message_template: str = """Онлайн-бронирование.

        Для оплаты бронирования перейдите в личный кабинет.
        {}

        www.strana.com"""
    email_template: str = "src/booking/templates/fast_booking.html"
    fast_booking_link_template: str = "https://{}/fast-booking/{}?token={}"

    def __init__(
        self,
        backend_config: dict[str, Any],
        booking_config: dict[str, Any],
        check_booking_task: Any,
        sms_class: Type[BookingSms],
        email_class: Type[BookingEmail],
        user_repo: Type[UserRepo],
        booking_repo: Type[BookingRepo],
        property_repo: Type[BookingPropertyRepo],
        building_booking_type_repo: buildings_repos.BuildingBookingTypeRepo,
        amocrm_class: Type[BookingAmoCRM],
        sql_request_class: Type[BookingSqlUpdateRequest],
        token_creator: Callable[[int], dict[str, Any]],
        import_property_service: Any,
        site_config: dict[str, Any],
        create_amocrm_contact_service: CreateContactService,
        global_id_encoder: Callable[[str, str], str],
        global_id_decoder: Callable[[str], tuple[str, Union[str, int]]],
        create_booking_log_task: Optional[Any] = None,
        logger: Optional[Any] = structlog.getLogger(__name__),
    ) -> None:
        self.logger = logger
        self.user_repo: UserRepo = user_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.property_repo: BookingPropertyRepo = property_repo()

        self.sms_class: Type[BookingSms] = sms_class
        self.check_booking_task: Any = check_booking_task
        self.email_class: Type[BookingEmail] = email_class
        self.amocrm_class: Type[BookingAmoCRM] = amocrm_class
        self.import_property_service: Any = import_property_service
        self.create_booking_log_task: Any = create_booking_log_task
        self.token_creator: Callable[[int], dict[str, Any]] = token_creator
        self.sql_request_class: Type[BookingSqlUpdateRequest] = sql_request_class
        self.create_amocrm_contact_service: CreateContactService = create_amocrm_contact_service

        self.global_id_encoder: Callable[[str, str], str] = global_id_encoder
        self.global_id_decoder: Callable[[str], tuple[str, Union[str, int]]] = global_id_decoder

        self.building_booking_type_repo: buildings_repos.BuildingBookingTypeRepo = building_booking_type_repo

        self.site_host: str = site_config["site_host"]
        self.fast_booking_time_hours: int = booking_config["fast_time_hours"]

        self.connection_options: dict[str, Any] = dict(
            user=backend_config["db_user"],
            host=backend_config["db_host"],
            port=backend_config["db_port"],
            database=backend_config["db_name"],
            password=backend_config["db_password"],
        )

    @amocrm_note(AmoCRM)
    async def __call__(
        self,
        *,
        booking: Optional[Booking],
        webhook_lead: WebhookLead,
        amocrm_stage: Optional[str],
        amocrm_substage: Optional[str],
    ) -> Tuple[Optional[Booking], bool]:
        if booking:
            notify_client = False
            if not booking.is_fast_booking():
                notify_client = True
                data = dict(tags=list(webhook_lead.tags.values()))
                booking = await self.booking_repo.update(booking, data)
                user: User = await booking.user
                await self._send_fast_booking_notify(user=user, booking=booking)
            return booking, notify_client
        async with await self.amocrm_class() as amocrm:
            lead: Optional[AmoLead] = await amocrm.fetch_lead(
                lead_id=webhook_lead.lead_id,
                query_with=[AmoLeadQueryWith.contacts],
            )
        self.logger.info(
            'Parsed data',
            lead_id=webhook_lead.lead_id,
            pipeline_id=webhook_lead.pipeline_id,
            new_status_id=webhook_lead.new_status_id,
        )

        lead_custom_fields = {
            field.field_id:
                CustomFieldValue(value=field.values[0].value, enum=field.values[0].enum_id)
            for field in lead.custom_fields_values
        }
        self._validate_lead(lead_custom_fields)

        property_id: str = webhook_lead.custom_fields.get(
            self.amocrm_class.property_field_id,
            CustomFieldValue(),
        ).value
        property_str_type = lead_custom_fields.get(
            self.amocrm_class.property_str_type_field_id, CustomFieldValue()
        ).value
        property_type: str = self.amocrm_class.property_str_type_reverse_values.get(property_str_type)
        booking_property: Property = await self._create_property(property_id, property_type)
        user: Optional[User] = None
        for contact in lead.embedded.contacts:
            if contact.is_main:
                user: User = await self._update_or_create_user_from_amo(contact.id)
                break
        if not user:
            self.logger.error("No main contact in lead", lead_id=webhook_lead.lead_id)
            return None, False
        booking_type_id = lead_custom_fields.get(
            self.amocrm_class.booking_type_field_id, CustomFieldValue()
        ).enum
        booking: Booking = await self._create_new_booking_from_amo(
            lead=lead,
            amocrm_stage=amocrm_stage,
            amocrm_substage=amocrm_substage,
            tags=list(webhook_lead.tags.values()),
            user=user,
            booking_property=booking_property,
            booking_type_id=booking_type_id,
        )
        await self._send_fast_booking_notify(user=user, booking=booking)
        return booking, True

    async def _send_fast_booking_notify(self, user: User, booking: Booking):
        token: str = self.token_creator(subject_type=user.type.value, subject=user.id)["token"]
        await self._send_sms(booking, user, token)
        await self._send_email(booking, user, token)

    def _validate_lead(self, lead_custom_fields: dict):
        """validate lead"""
        errors = []
        if self.amocrm_class.city_field_id not in lead_custom_fields:
            errors.append("Город")
        if self.amocrm_class.property_field_id not in lead_custom_fields:
            errors.append("Объект недвижимости")
        if self.amocrm_class.booking_type_field_id not in lead_custom_fields:
            errors.append("Условие оплаты брони")
        if len(errors) > 0:
            raise BookingRequestValidationError(message=f"Не заполнены поля: {', '.join(errors)}")

    async def _create_property(
        self,
        property_id: str,
        property_type: Optional[str] = None,
    ) -> Property:
        """
        Create property for booking
        """
        global_property_type: str = self.amocrm_class.global_types_mapping[property_type]
        property_global_id: str = self.global_id_encoder(
            global_property_type, property_id
        )

        filters: dict[str, Any] = dict(global_id=property_global_id)
        data: dict[str, Any] = dict(premise=PremiseType.RESIDENTIAL, type=property_type)
        if property_type != PropertyTypes.FLAT:
            data: dict[str, Any] = dict(premise=PremiseType.NONRESIDENTIAL, type=property_type)
        booking_property: Property = await self.property_repo.update_or_create(filters=filters, data=data)
        await self.import_property_service(property=booking_property)
        filters = dict(id=booking_property.id)
        related_fields = ["building"]
        booking_property: Property = await self.property_repo.retrieve(
            filters=filters,
            related_fields=related_fields)
        return booking_property

    async def _update_or_create_user_from_amo(self, main_contact_id: int) -> User:
        """
        Update or create user from amo
        """
        async with await self.amocrm_class() as amocrm:
            contact: Optional[AmoContact] = await amocrm.fetch_contact(user_id=main_contact_id)

        amo_user_data: dict = self.create_amocrm_contact_service.fetch_amocrm_data(contact)
        self.validate_contact(amo_user_data)
        user_filters: dict[str, Any] = dict(phone=amo_user_data.pop("phone", None), type=UserType.CLIENT)
        partial_user_data: dict[str, Any] = dict(
            is_brokers_client=True,
            is_deleted=False,
            is_active=True,
        )
        amo_user_data.update(partial_user_data)

        user: User = await self.user_repo.update_or_create(filters=user_filters, data=amo_user_data)
        self.logger.info('AMOCRM User', amocrm_id=main_contact_id, user_id=user.id, phone=user.phone)

        return user

    def validate_contact(self, contact: dict):
        """validate contact"""
        errors = []
        if not all((contact.get('passport_series'), contact.get('passport_series'))):
            errors.append('Паспорт: серия и номер')
        if not contact.get('birth_date'):
            errors.append('День рождения')
        if len(errors) > 0:
            raise BookingRequestValidationError(message=f"Не заполнены поля: {', '.join(errors)}")

    async def _create_new_booking_from_amo(
        self, *, lead: AmoLead, amocrm_stage: str, amocrm_substage: str,
            tags: list[str], user: User, booking_property: Property,
            booking_type_id: Optional[str],
    ) -> Booking:
        """
        New booking creation
        """
        booking_data: dict = {}

        selected_booking_type: Optional[Union[BuildingBookingType, BookingTypeNamedTuple]] = \
            await self.building_booking_type_repo.retrieve(filters=dict(amocrm_id=booking_type_id))
        building: Optional[Building] = booking_property.building

        if selected_booking_type is None:
            selected_booking_type = BookingTypeNamedTuple(
                price=building.booking_price, period=building.booking_period,
            )

        expires = datetime.now(tz=UTC) + timedelta(hours=self.fast_booking_time_hours)
        should_be_deactivated_by_timer = True
        booking_data.update(
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
            expires=expires,
            tags=tags,
            should_be_deactivated_by_timer=should_be_deactivated_by_timer,
            profitbase_booked=True,
            created_source=BookingCreatedSources.FAST_BOOKING,
            active=True,
        )

        booking: Booking = await self.booking_repo.create(booking_data)
        self.logger.info('New Booking created', lead_id=lead.id, booking_id=booking.id, tags=booking.tags)

        await self._property_backend_booking(booking=booking)

        task_delay: int = (booking.expires - datetime.now(tz=UTC)).seconds
        self.check_booking_task.apply_async((booking.id,), countdown=task_delay)

        return booking

    # @logged_action(content="БРОНИРОВАНИЕ | PORTAL")
    async def _property_backend_booking(self, booking: Booking) -> str:
        """
        Property booked
        """
        _, property_id = self.global_id_decoder(global_id=booking.property.global_id)
        request_options: dict[str, Any] = dict(
            table="properties_property",
            filters=dict(id=property_id),
            data=dict(status=booking.property.statuses.BOOKED),
            connection_options=self.connection_options,
        )
        async with self.sql_request_class(**request_options) as response:
            result: str = response
        return result

    async def _send_sms(self, booking: Booking, user: User, token: str) -> Task:
        """
        Send sms
        """
        fast_booking_link: str = self.fast_booking_link_template.format(self.site_host, booking.id, token)
        message: str = self.sms_message_template.format(fast_booking_link)
        sms_options: dict[str, Any] = dict(phone=user.phone, message=message)
        sms_service: BookingSms = self.sms_class(**sms_options)
        return sms_service.as_task()

    async def _send_email(self, booking: Booking, user: User, token: str) -> Task:
        """
        Send email
        """
        fast_booking_link: str = self.fast_booking_link_template.format(self.site_host, booking.id, token)
        email_options: dict[str, Any] = dict(
            topic="Ссылка на онлайн-бронирование",
            recipients=[user.email],
            template=self.email_template,
            context=dict(fast_booking_link=fast_booking_link),
        )
        email_service: BookingEmail = self.email_class(**email_options)
        return email_service.as_task()