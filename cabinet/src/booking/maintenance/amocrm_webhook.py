# pylint: disable=broad-except
import traceback
import pytz
from datetime import datetime
from functools import wraps
from typing import Any, Union
from urllib.parse import parse_qs, unquote
import structlog

from common.amocrm import AmoCRM
from config import EnvTypes, maintenance_settings

logger = structlog.get_logger("amocrm_webhook_maintenance")


def _fetch_tags(
    data: dict[str, Any]
) -> tuple:
    """
    parse webhook data
    """
    result: dict[str, Union[int, list[int]]] = dict(amocrm_id=None, tags=[])
    for key, value in data.items():
        if "tags" in key:
            if "id" in key:
                result["tags"].append(int(value[0]))
        elif key in {
            "leads[status][0][id]",
            "leads[update][0][id]",
            "leads[create][0][id]",
            "leads[add][0][id]",
        }:
            result["amocrm_id"] = int(value[0])
    return result["amocrm_id"], result["tags"]


def amocrm_webhook_maintenance(amocrm_webhook):
    """
    maintenance for amocrm webhook
    """

    @wraps(amocrm_webhook)
    async def wrapper(request, *args, **kwargs):
        data: dict[str, Any] = parse_qs(unquote((await request.body()).decode("utf-8")))
        amocrm_id, tags = _fetch_tags(data)
        logger.info(f"[{datetime.now(tz=pytz.UTC)}] AMOCRM webhook maintenance: id={amocrm_id} tags={tags}")
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
            return await amocrm_webhook(request, *args, **kwargs)
        except Exception:
            traceback.print_exc()
            return

    return wrapper
