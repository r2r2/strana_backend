# pylint: disable=inconsistent-return-statements
from asyncio import Task
from typing import Any, Optional, Type, Callable, Union

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoLeadQueryWith
from common.amocrm.exceptions import (AmoContactIncorrectPhoneFormatError,
                                      AmoNoContactError)
from common.amocrm.types import AmoContact, AmoCustomField, AmoLead
from common.amocrm.types.lead import AmoLeadContact
from common.utils import parse_phone
from src.booking.entities import BaseBookingCase
from src.booking.exceptions import BookingNotFoundError
from src.booking.maintenance import amocrm_sms_maintenance, amocrm_webhook_maintenance as maintenance
from src.booking.repos import Booking, BookingRepo
from src.booking.types import BookingAmoCRM, BookingSms
from src.users.repos import User
from ..maintenance.amocrm_sms_note import amocrm_sms_note


class AmoCRMSmsWebhookCase(BaseBookingCase):
    """Вебхук для отправки смс главному контакту сделки"""
    sms_message_template: str = """Онлайн-бронирование.

         Для оплаты бронирования перейдите в личный кабинет.
         {}

         www.strana.com"""
    fast_booking_link_template: str = "https://{}/fast-booking/{}?token={}"

    def __init__(
        self,
        amocrm_class: Type[BookingAmoCRM],
        sms_class: Type[BookingSms],
        booking_repo: Type[BookingRepo],
        site_config: dict[str, Any],
        token_creator: Callable[..., dict[str, str]],
    ):
        self.amocrm = amocrm_class
        self.sms_class = sms_class
        self.booking_repo = booking_repo()
        self.site_host: str = site_config["site_host"]
        self.token_creator: Callable[..., dict[str, str]] = token_creator

    @amocrm_sms_maintenance
    @amocrm_sms_note(AmoCRM)
    async def __call__(self, amocrm_id: int) -> None:
        """Отправка смс"""
        booking: Optional[Booking] = await self.booking_repo.retrieve(
            filters=dict(amocrm_id=amocrm_id)
        ).only('id', 'user')
        if not booking:
            raise BookingNotFoundError

        async with await self.amocrm() as amocrm:
            lead: AmoLead = await self._get_lead(amocrm, amocrm_id)
            main_contact: AmoContact = await self._get_main_contact(amocrm, lead)
            phone: str = self._get_phone_by_contact(amocrm, main_contact)

        user: User = await booking.user
        token: str = self.token_creator(subject_type=user.type.value, subject=user.id)["token"]
        await self._send_sms(phone, booking, token)

    async def _get_lead(self, amocrm, lead_id: int) -> AmoLead:
        """Получение сделки по id"""
        lead: Optional[AmoLead] = await amocrm.fetch_lead(
            lead_id=lead_id,
            query_with=[AmoLeadQueryWith.contacts],
        )
        if not lead:
            raise BookingNotFoundError
        return lead

    async def _get_main_contact(self, amocrm, lead: AmoLead) -> AmoContact:
        """Получение главного контакта у сделки"""
        main_contact: Optional[AmoLeadContact] = None
        for contact in lead.embedded.contacts:
            if contact.is_main:
                main_contact = contact
                break
        if not main_contact:
            raise AmoNoContactError

        main_contact: AmoContact = await amocrm.fetch_contact(user_id=main_contact.id)

        if not main_contact:
            raise AmoNoContactError

        return main_contact

    def _get_phone_by_contact(self, amocrm, contact: AmoContact) -> str:
        """Получение телефона у главного контакта"""
        custom_fields: list[AmoCustomField] = contact.custom_fields_values
        for custom_field in custom_fields:
            if custom_field.field_id == amocrm.phone_field_id:
                phone: Optional[str] = custom_field.values[0].value
                if phone:
                    phone: Optional[str] = parse_phone(phone)
                if phone is None:
                    print(f"Amo send incorrect phone format: {phone}")
                    raise AmoContactIncorrectPhoneFormatError
                return phone

    def _send_sms(self, phone: str, booking: Booking, token: str) -> Task:
        """СМС уведомление"""
        fast_booking_link: str = self.fast_booking_link_template.format(self.site_host, booking.id, token)
        message: str = self.sms_message_template.format(fast_booking_link)
        sms_options: dict[str, Any] = dict(phone=phone, message=message)
        sms_service: Any = self.sms_class(**sms_options)
        return sms_service.as_task()
