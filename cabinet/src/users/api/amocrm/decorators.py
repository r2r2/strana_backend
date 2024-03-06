from typing import Any
from urllib.parse import parse_qs, unquote

import sentry_sdk
import structlog
from functools import wraps

from common.amocrm import AmoCRM
from config import maintenance_settings, EnvTypes

logger = structlog.get_logger("amocrm_contact_webhook_maintenance")


def _fetch_contact_tags(data: dict[str, Any]) -> list:
    tags = []
    for key, value in data.items():
        if "tags" in key:
            if "id" in key:
                tags.append(int(value[0]))
    return tags


def amocrm_contact_webhook_maintenance(amocrm_client_webhook):
    @wraps(amocrm_client_webhook)
    async def wrapper(request, *args, **kwargs):
        data: dict[str, Any] = parse_qs(unquote((await request.body()).decode("utf-8")))
        tags = _fetch_contact_tags(data)
        if maintenance_settings["environment"] == EnvTypes.DEV:
            if AmoCRM.dev_contact_tag_id not in tags:
                logger.info("amocrm_client_webhook in DEV-mode")
                return None
        elif maintenance_settings["environment"] == EnvTypes.STAGE:
            if AmoCRM.stage_contact_tag_id not in tags:
                logger.info("amocrm_client_webhook in STAGE-mode")
                return None
        elif maintenance_settings["environment"] == EnvTypes.PROD:
            if AmoCRM.dev_contact_tag_id in tags or AmoCRM.stage_contact_tag_id in tags:
                logger.info("amocrm_client_webhook in PROD-mode")
                return None

        try:
            return await amocrm_client_webhook(request, *args, **kwargs)
        except Exception as exc:
            sentry_sdk.capture_exception(exc)
            return

    return wrapper

