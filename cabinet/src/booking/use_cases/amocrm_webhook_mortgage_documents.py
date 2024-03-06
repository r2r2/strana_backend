import asyncio
from typing import Any, Union, Optional, Callable
from urllib.parse import parse_qs, unquote

import structlog

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoLeadQueryWith
from common.amocrm.exceptions import AmoNoMainContactError
from common.amocrm.types import AmoLead, AmoContact
from common.messages import SmsService
from common.schemas import UrlEncodeDTO
from common.utils import generate_notify_url
from config import site_config
from src.amocrm.repos import AmocrmStatus, AmocrmStatusRepo
from src.booking.constants import BookingStagesMapping, BookingCreatedSources
from src.booking.event_emitter_handlers import event_emitter
from src.booking.repos import Booking, BookingRepo, BookingSource
from src.booking.types import WebhookLead, CustomFieldValue
from src.booking.utils import get_booking_source
from src.notifications.services import GetSmsTemplateService
from src.users.constants import UserType
from src.users.repos import User, UserRepo
from src.users.services import CreateContactService


class MortgageDocumentsWebhookCase:
    CLIENT_ROLE_SLUG: str = UserType.CLIENT
    SMS_EVENT_SLUG: str = "mortgage_documents"
    SITE_HOST: str = site_config["site_host"]
    REDIRECT_URL: str = "/mortgage"
    PATH: str = "/token-auth"

    def __init__(
        self,
        booking_repo: type[BookingRepo],
        sms_template_service: GetSmsTemplateService,
        sms_class: type[SmsService],
        token_creator: Callable[[str, int], dict[str, Any]],
        amocrm: type[AmoCRM],
        create_amocrm_contact_service: CreateContactService,
        user_repo: type[UserRepo],
        statuses_repo: type[AmocrmStatusRepo],
    ):
        self.booking_repo: BookingRepo = booking_repo()
        self.sms_template_service: GetSmsTemplateService = sms_template_service
        self.sms_class: type[SmsService] = sms_class
        self.token_creator: Callable[[str, int], dict[str, Any]] = token_creator
        self.amocrm: type[AmoCRM] = amocrm
        self.create_amocrm_contact_service: CreateContactService = create_amocrm_contact_service
        self.user_repo: UserRepo = user_repo()
        self.statuses_repo: AmocrmStatusRepo = statuses_repo()

        self.logger: structlog.BoundLogger = structlog.get_logger(self.__class__.__name__)

    async def __call__(self, payload: bytes) -> None:
        data: dict[str, Any] = parse_qs(unquote(payload.decode("utf-8")))
        self.logger.info("Получен вебхук из АМО на 'Сбор документов':", data=data)
        webhook_lead: WebhookLead = self._parse_data(data=data)

        booking: Booking = await self._get_booking(lead_id=webhook_lead.lead_id)
        await self._notify_client(user=booking.user)

    async def _get_booking(self, lead_id: int) -> Booking:
        booking: Booking = await self.booking_repo.retrieve(
            filters=dict(amocrm_id=lead_id),
            related_fields=["user"],
        )
        if not booking:
            self.logger.info("No booking found. Creating new booking.", lead_id=lead_id)
            booking: Booking = await self._create_booking(lead_id=lead_id)
        return booking

    async def _create_booking(self, lead_id: int) -> Booking:
        async with await self.amocrm() as amocrm:
            lead: AmoLead = await amocrm.fetch_lead(
                lead_id=lead_id,
                query_with=[AmoLeadQueryWith.contacts],
            )
            user: User = await self._get_user(lead=lead, amocrm=amocrm)

        tags: set[str] = {tag.name for tag in lead.embedded.tags}
        amocrm_substage: str | None = AmoCRM.get_lead_substage(lead.status_id)
        amocrm_stage: str | None = BookingStagesMapping()[amocrm_substage]
        amocrm_status: AmocrmStatus | None = await self.statuses_repo.retrieve(
            filters=dict(id=lead.status_id)
        )
        booking_source: BookingSource = await get_booking_source(slug=BookingCreatedSources.AMOCRM)

        booking_data: dict[str, Any] = dict(
            amocrm_id=lead.id,
            user=user,
            amocrm_stage=amocrm_stage,
            amocrm_substage=amocrm_substage,
            amocrm_status=amocrm_status,
            booking_source=booking_source,
            tags=list(tags),
            origin=f"https://{self.SITE_HOST}"
        )

        booking: Booking = await self.booking_repo.create(data=booking_data)
        event_emitter.ee.emit(event='booking_created', booking=booking)
        await booking.fetch_related("user")
        self.logger.info("New Booking created", booking_id=booking.id, lead_id=lead.id)

        return booking

    async def _get_user(self, lead: AmoLead, amocrm: AmoCRM) -> User:
        user: User | None = None
        for contact in lead.embedded.contacts:
            if contact.is_main:
                user: User = await self._update_or_create_user_from_amo(
                    main_contact_id=contact.id,
                    amocrm=amocrm,
                )
                return user
        if not user:
            self.logger.info("No main contact in lead", lead_id=lead.id)
            raise AmoNoMainContactError

    async def _update_or_create_user_from_amo(self, main_contact_id: int, amocrm: AmoCRM) -> User:
        """
        Update or create user from amo
        """
        amo_user_data: dict[str, Any] = await self.get_amocrm_user_data(
            main_contact_id=main_contact_id,
            amocrm=amocrm,
        )
        partial_user_data = dict(
            is_brokers_client=True,
            is_deleted=False,
            is_active=True,
        )
        amo_user_data.update(partial_user_data)
        user: User | None = await self.update_user(amo_user_data, main_contact_id)

        if not user:
            user: User = await self.create_user(amo_user_data, main_contact_id)

        return user

    async def get_amocrm_user_data(self, main_contact_id: int, amocrm: AmoCRM) -> dict:
        contact: AmoContact | None = await amocrm.fetch_contact(user_id=main_contact_id)
        return await self.create_amocrm_contact_service.fetch_amocrm_data(contact)

    async def update_user(self, amo_user_data: dict, main_contact_id: int) -> User | None:
        user_filters = dict(amocrm_id=main_contact_id, role__slug=UserType.CLIENT)
        user: User = await self.user_repo.retrieve(filters=user_filters)
        if user:
            self.logger.info('Updating user from AMOCRM', amocrm_id=main_contact_id, user_id=user.id)
            return await self.user_repo.update(model=user, data=amo_user_data)

    async def create_user(self, amo_user_data: dict, main_contact_id: int) -> User:
        amo_user_data.update({"amocrm_id": main_contact_id})
        user: User = await self.user_repo.retrieve(
            filters=dict(phone=amo_user_data["phone"], role__slug=UserType.CLIENT)
        )
        if user:
            self.logger.info('Updating user:', amocrm_id=main_contact_id, user_id=user.id)
            return await self.user_repo.update(model=user, data=amo_user_data)
        else:
            self.logger.info('Creating user:', amocrm_id=main_contact_id)
            return await self.user_repo.create(data=amo_user_data)

    async def _notify_client(self, user: User) -> None:
        token: str = self.token_creator(subject_type=self.CLIENT_ROLE_SLUG, subject=user.id)["token"]
        await self._send_sms(user, token)

    async def _send_sms(self, user: User, token: str) -> asyncio.Task:
        """
        Send sms
        """
        sms_notification_template = await self.sms_template_service(
            sms_event_slug=self.SMS_EVENT_SLUG,
        )
        if sms_notification_template and sms_notification_template.is_active:
            query_params: dict[str, Any] = dict(
                redirect_url=self.REDIRECT_URL,
                token=token,
            )
            data: dict[str, Any] = dict(
                host=self.SITE_HOST,
                route_template=self.PATH,
                query_params=query_params,
                use_ampersand_ascii=True,
            )
            url_dto: UrlEncodeDTO = UrlEncodeDTO(**data)
            link: str = generate_notify_url(url_dto=url_dto)

            sms_options: dict[str, Any] = dict(
                phone=user.phone,
                message=sms_notification_template.template_text.format(link=link),
                lk_type=sms_notification_template.lk_type.value,
                sms_event_slug=sms_notification_template.sms_event_slug,
            )

            sms_service: SmsService = self.sms_class(**sms_options)
            self.logger.info('Mortgage documents SMS sent', phone=user.phone, message=sms_options["message"])
            return sms_service.as_task()

    @staticmethod
    def _parse_data(
        data: dict[str, Any]
    ) -> WebhookLead:
        lead_id: Optional[int] = None
        pipeline_id: Optional[int] = None
        new_status_id: Optional[int] = None
        tags: dict[str, Any] = {}
        custom_fields: dict[str, Any] = {}
        for key, value in data.items():
            if "custom_fields" in key:
                key_components: list[str] = key.split("[")
                if len(key_components) >= 5:
                    field_number: str = key_components[4][:-1]
                    if field_number not in custom_fields:
                        custom_fields[field_number]: dict[str, Any] = {}
                    # проверяем, что пришло поле id и никакое другое (не account_id, type_id и т.д)
                    # иначе id-перезаписываются, т.к у всех полей есть account_id - одинаковый,
                    if key.split("[")[-1] == "id]":
                        custom_fields[field_number]["id"]: Union[str, int] = int(value[0])
                    if "name" in key:
                        custom_fields[field_number]["name"]: Union[str, int] = value[0]
                    if "values" in key:
                        _, value_enum = key.split("values")
                        if "value" in value_enum:
                            custom_fields[field_number]["value"]: Union[str, int] = value[0]
                        if "enum" in value_enum:
                            custom_fields[field_number]["enum"]: Union[str, int] = int(value[0])
            elif "tags" in key:
                key_components: list[str] = key.split("[")
                if len(key_components) >= 5:
                    field_number: str = key_components[4][:-1]
                    if field_number not in tags:
                        tags[field_number]: dict[str, Any] = {}
                    if "id" in key:
                        tags[field_number]["id"] = int(value[0])
                    if "name" in key:
                        tags[field_number]["name"] = value[0]

            elif key in {
                "leads[sensei][0][id]",
            }:
                lead_id = int(value[0])
            elif key in {
                "leads[sensei][0][status_id]",
            }:
                new_status_id = int(value[0])
            elif key in {
                "leads[sensei][0][pipeline_id]",
            }:
                pipeline_id = int(value[0])
        custom_fields_dict: dict[int, CustomFieldValue] = {
            field["id"]: CustomFieldValue(
                name=field.get("name"),
                value=field.get("value"),
                enum=field.get("enum"),
            )
            for field in custom_fields.values()
        }
        tags_dict: dict[int, str] = {tag.get("id"): tag.get("name") for tag in tags.values()}

        lead = WebhookLead(
            lead_id=lead_id,
            pipeline_id=pipeline_id,
            new_status_id=new_status_id,
            custom_fields=custom_fields_dict,
            tags=tags_dict,
        )
        return lead
