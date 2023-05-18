# pylint: disable=inconsistent-return-statements
from asyncio import Task
from typing import Any, Optional, Type

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoLeadQueryWith
from common.amocrm.exceptions import (AmoContactIncorrectPhoneFormatError,
                                      AmoNoContactError)
from common.amocrm.types import AmoContact, AmoCustomField, AmoLead
from common.amocrm.types.lead import AmoLeadContact
from common.utils import parse_phone
from src.booking.entities import BaseBookingCase
from src.booking.exceptions import (BookingIdWasNotFoundError,
                                    BookingNotFoundError)
from src.booking.maintenance import amocrm_sms_maintenance, amocrm_webhook_maintenance as maintenance
from src.booking.types import BookingAmoCRM, BookingSms
from ..maintenance.amocrm_sms_note import amocrm_sms_note


class AmoCRMSmsWebhookCase(BaseBookingCase):
    """Вебхук для отправки смс главному контакту сделки"""

    def __init__(
        self,
        amocrm_class: Type[BookingAmoCRM],
        sms_class: Type[BookingSms],
    ):
        self.amocrm = amocrm_class
        self.sms_class = sms_class

    @amocrm_sms_maintenance
    @amocrm_sms_note(AmoCRM)
    async def __call__(self, amocrm_id: int) -> None:

        async with await self.amocrm() as amocrm:
            lead: AmoLead = await self._get_lead(amocrm, amocrm_id)
            main_contact: AmoContact = await self._get_main_contact(amocrm, lead)
            phone: str = self._get_phone_by_contact(amocrm, main_contact)

        await self._send_sms(phone)

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

    def _send_sms(self, phone: str) -> Task:
        """СМС уведомление"""
        # copied from webhook deal_success
        message = (
            "Покупка квартиры.\n\n"
            "Договор был подписан и сделка состоялась.\n\n"
            "Подробности в личном кабинете:\n"
            "www.strana.com/login"
        )
        sms_options: dict[str, Any] = dict(phone=phone, message=message)
        sms_service: Any = self.sms_class(**sms_options)
        return sms_service.as_task()
