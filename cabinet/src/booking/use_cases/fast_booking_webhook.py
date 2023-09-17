from asyncio import Task
from datetime import datetime, timedelta
from typing import Any, Callable, Optional, Type, Union

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
from src.booking.loggers.wrappers import booking_changes_logger
from src.amocrm.repos import AmocrmStatus, AmocrmStatusRepo
from src.booking.utils import get_booking_reserv_time, get_booking_source

from ...users.services import CreateContactService
from ..constants import BookingCreatedSources, BookingStagesMapping
from ..entities import BaseBookingCase
from ..exceptions import BookingRequestValidationError
from ..maintenance.amocrm_leed_note import amocrm_note
from ..mixins import BookingLogMixin
from src.booking.repos import Booking, BookingRepo, BookingSource
from ..types import (BookingAmoCRM, BookingEmail, BookingPropertyRepo,
                     BookingSms, BookingSqlUpdateRequest,
                     BookingTypeNamedTuple, CustomFieldValue)
from src.notifications.services import GetSmsTemplateService, GetEmailTemplateService


class FastBookingWebhookCase(BaseBookingCase, BookingLogMixin):
    """
    Обработка быстрой брони по вебхуку
    """

    sms_event_slug = "booking_amo_webhook"
    mail_event_slug: str = "booking_amo_webhook"
    fast_booking_link_template: str = "https://{}/fast-booking/{}?token={}"

    def __init__(
        self,
        backend_config: dict[str, Any],
        check_booking_task: Any,
        sms_class: Type[BookingSms],
        email_class: Type[BookingEmail],
        user_repo: Type[UserRepo],
        booking_repo: Type[BookingRepo],
        property_repo: Type[BookingPropertyRepo],
        statuses_repo: Type[AmocrmStatusRepo],
        building_booking_type_repo: buildings_repos.BuildingBookingTypeRepo,
        amocrm_class: Type[BookingAmoCRM],
        sql_request_class: Type[BookingSqlUpdateRequest],
        token_creator: Callable[[int], dict[str, Any]],
        import_property_service: Any,
        site_config: dict[str, Any],
        create_amocrm_contact_service: CreateContactService,
        global_id_encoder: Callable[[str, str], str],
        global_id_decoder: Callable[[str], tuple[str, Union[str, int]]],
        get_sms_template_service: GetSmsTemplateService,
        get_email_template_service: GetEmailTemplateService,
        create_booking_log_task: Optional[Any] = None,
        logger: Optional[Any] = structlog.getLogger(__name__),
    ) -> None:
        self.logger = logger
        self.booking: Optional[Booking] = None
        self.user_repo: UserRepo = user_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.property_repo: BookingPropertyRepo = property_repo()
        self.statuses_repo: AmocrmStatusRepo = statuses_repo()

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
        self.get_sms_template_service: GetSmsTemplateService = get_sms_template_service
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service

        self.connection_options: dict[str, Any] = dict(
            user=backend_config["db_user"],
            host=backend_config["db_host"],
            port=backend_config["db_port"],
            database=backend_config["db_name"],
            password=backend_config["db_password"],
        )

        self.booking_update_or_create = booking_changes_logger(
            self.booking_repo.update_or_create, self, content="Создание или обновление"
        )
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="Изменение быстрой брони"
        )
        self.booking_create = booking_changes_logger(
            self.booking_repo.create, self, content="Создание быстрой брони"
        )

    @amocrm_note(AmoCRM)
    async def __call__(
        self,
        *,
        booking: Optional[Booking] = None,
        amocrm_id: Optional[int] = None,
        amocrm_stage: Optional[str] = None,
        amocrm_substage: Optional[str] = None,
    ) -> Optional[Booking]:
        self.booking = booking

        async with await self.amocrm_class() as amocrm:
            lead: Optional[AmoLead] = await amocrm.fetch_lead(
                lead_id=amocrm_id,
                query_with=[AmoLeadQueryWith.contacts],
            )

        if self.booking:
            await self.booking_update(booking=booking, data=dict(tags=[tag.name for tag in lead.embedded.tags]))

        self.logger.info(
            'Parsed data',
            lead_id=lead.id,
            pipeline_id=lead.pipeline_id,
            new_status_id=lead.status_id,
        )

        lead_custom_fields = {
            field.field_id:
                CustomFieldValue(value=field.values[0].value, enum=field.values[0].enum_id)
            for field in lead.custom_fields_values
        }

        self._validate_lead(lead_custom_fields)

        property_id: str = lead_custom_fields.get(
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
            self.logger.error("No main contact in lead", lead_id=lead.id)
            return None
        booking_type_id = lead_custom_fields.get(
            self.amocrm_class.booking_type_field_id, CustomFieldValue()
        ).enum
        fast_booking: Booking = await self._create_new_booking_from_amo(
            lead=lead,
            lead_custom_fields=lead_custom_fields,
            user=user,
            booking_property=booking_property,
            booking_type_id=booking_type_id,
        )
        await self._send_fast_booking_notify(user=user, booking=fast_booking)
        return fast_booking

    async def _send_fast_booking_notify(self, user: User, booking: Booking) -> None:
        token: str = self.token_creator(subject_type=user.type.value, subject=user.id)["token"]
        await self._send_sms(booking, user, token)
        await self._send_email(booking, user, token)

    def _validate_lead(self, lead_custom_fields: dict):
        """
        Validate lead
        """
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
        global_property_type: str = self.amocrm_class.global_types_mapping.get(property_type, "GlobalFlatType")
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
        related_fields = ["building", "project"]
        booking_property: Property = await self.property_repo.retrieve(
            filters=filters,
            related_fields=related_fields
        )
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
        self,
        *,
        lead: AmoLead,
        lead_custom_fields: dict[int, Any],
        user: User,
        booking_property: Property,
        booking_type_id: Optional[str],
    ) -> Booking:
        """
        New booking creation
        """
        selected_booking_type: Optional[Union[BuildingBookingType, BookingTypeNamedTuple]] = \
            await self.building_booking_type_repo.retrieve(filters=dict(amocrm_id=booking_type_id))
        building: Optional[Building] = booking_property.building

        if selected_booking_type is None:
            selected_booking_type = BookingTypeNamedTuple(
                price=building.booking_price, period=building.booking_period,
            )

        amocrm_substage: Optional[str] = AmoCRM.get_lead_substage(lead.status_id)
        amocrm_stage: Optional[str] = BookingStagesMapping()[amocrm_substage]
        amocrm_status: Optional[AmocrmStatus] = await self.statuses_repo.retrieve(
            filters=dict(id=lead.status_id)
        )

        created_source = BookingCreatedSources.FAST_BOOKING
        booking_source: BookingSource = await get_booking_source(slug=BookingCreatedSources.FAST_BOOKING)
        booking_reserv_time: float = await get_booking_reserv_time(
            created_source=booking_source.slug,
            booking_property=booking_property,
        )
        expires = datetime.now(tz=UTC) + timedelta(hours=booking_reserv_time)
        should_be_deactivated_by_timer = True
        booking_data: dict[str, Any] = dict(
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
            should_be_deactivated_by_timer=should_be_deactivated_by_timer,
            profitbase_booked=True,
            created_source=created_source,  # todo: deprecated
            booking_source=booking_source,
            active=True,
        )

        property_final_price: Optional[int] = lead_custom_fields.get(
            self.amocrm_class.property_final_price_field_id, CustomFieldValue()
        ).value
        price_with_sale: Optional[int] = lead_custom_fields.get(
            self.amocrm_class.property_price_with_sale_field_id, CustomFieldValue()
        ).value

        if property_final_price or price_with_sale:
            booking_data.update(
                final_payment_amount=property_final_price or price_with_sale,
            )

        if self.booking:
            booking: Booking = await self.booking_update(booking=self.booking, data=booking_data)
            self.logger.info('Booking updated', lead_id=lead.id, booking_id=booking.id, tags=booking.tags)
        else:
            booking = await self.booking_create(data=booking_data)
            self.logger.info('New Booking created', lead_id=lead.id, booking_id=booking.id, tags=booking.tags)

        await self._property_backend_booking(booking=booking)

        if property_final_price or price_with_sale:
            data = dict(final_price=price_with_sale or property_final_price)
            await self.property_repo.update(model=booking_property, data=data)

        self.check_booking_task.apply_async((booking.id,), eta=booking.expires)

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
        sms_notification_template = await self.get_sms_template_service(
            sms_event_slug=self.sms_event_slug,
        )
        if sms_notification_template and sms_notification_template.is_active:
            fast_booking_link: str = self.fast_booking_link_template.format(self.site_host, booking.id, token)
            sms_options: dict[str, Any] = dict(
                phone=user.phone,
                message=sms_notification_template.template_text.format(fast_booking_link=fast_booking_link),
                lk_type=sms_notification_template.lk_type.value,
                sms_event_slug=sms_notification_template.sms_event_slug,
            )
            sms_service: BookingSms = self.sms_class(**sms_options)
            return sms_service.as_task()

    async def _send_email(self, booking: Booking, user: User, token: str) -> Task:
        """
        Send email
        """
        fast_booking_link: str = self.fast_booking_link_template.format(self.site_host, booking.id, token)
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.mail_event_slug,
            context=dict(fast_booking_link=fast_booking_link),
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=[user.email],
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: BookingEmail = self.email_class(**email_options)
            return email_service.as_task()
