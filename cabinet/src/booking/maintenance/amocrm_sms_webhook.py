import traceback
from datetime import datetime
from functools import wraps
import pytz
import structlog
from common.amocrm import AmoCRM
from config import EnvTypes, maintenance_settings
from typing import Optional
from common.amocrm.types import AmoLead
from common.amocrm.constants import AmoLeadQueryWith
from src.booking.exceptions import (BookingIdWasNotFoundError,
                                    BookingNotFoundError)


logger = structlog.get_logger("amocrm_sms_maintenance")


def amocrm_sms_maintenance(amocrm_sms_webhook):
    """
    maintenance for amocrm sms webhook
    """

    @wraps(amocrm_sms_webhook)
    async def wrapper_sms(self, amocrm_id: int):
        logger.info(
            f" AMOCRM sms maintenance PAYLOAD: payload={amocrm_id} ")
        amocrm_class = AmoCRM
        async with await amocrm_class() as amocrm:
            webhook_lead: Optional[AmoLead] = await amocrm.fetch_lead(lead_id=amocrm_id,
                                                                      query_with=[AmoLeadQueryWith.contacts])
        if not webhook_lead:
            logger.info(
                f"[{datetime.now(tz=pytz.UTC)}] AMOCRM sms maintenance lead_id NOT FOUND: lead_id={webhook_lead} ")
            raise BookingNotFoundError
        tags = webhook_lead.embedded.tags
        logger.info(f"[{datetime.now(tz=pytz.UTC)}] AMOCRM sms maintenance: amocrm_id={amocrm_id} tags={tags}")
        if maintenance_settings["environment"] == EnvTypes.DEV:
            if AmoCRM.fast_booking_tag_id in tags and AmoCRM.dev_booking_tag_id not in tags:
                return None
        elif maintenance_settings["environment"] == EnvTypes.STAGE:
            if AmoCRM.fast_booking_tag_id in tags and AmoCRM.stage_booking_tag_id not in tags:
                return None
        elif maintenance_settings["environment"] == EnvTypes.PROD:
            if (AmoCRM.fast_booking_tag_id in tags
                    and (AmoCRM.dev_booking_tag_id in tags or AmoCRM.stage_booking_tag_id in tags)):
                return None
        try:
            return await amocrm_sms_webhook(self, amocrm_id=amocrm_id)
        except Exception:
            traceback.print_exc()
            return

    return wrapper_sms


