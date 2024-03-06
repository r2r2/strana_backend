# pylint: disable=broad-except
import traceback
import pytz
from datetime import datetime
from functools import wraps
from typing import Any, Union
from urllib.parse import parse_qs, unquote

import sentry_sdk
import structlog

from common.amocrm import AmoCRM
from common.sentry.utils import send_sentry_log
from common.unleash.client import UnleashClient
from config import EnvTypes, maintenance_settings
from config.feature_flags import FeatureFlags

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
        body = await request.body()
        data: dict[str, Any] = parse_qs(unquote(body.decode("utf-8")))
        if UnleashClient().is_enabled(FeatureFlags.amo_webhook_request):
            logger.info(f"request body: {body}")
            logger.info(f"request data: {data}")
        amocrm_id, tags = _fetch_tags(data)
        logger.info(f"[{datetime.now(tz=pytz.UTC)}] AMOCRM webhook maintenance: id={amocrm_id} tags={tags}")
        sentry_ctx: dict[str, Any] = dict(
            tags=tags,
            data=data,
        )
        if maintenance_settings["environment"] == EnvTypes.DEV:
            if AmoCRM.dev_booking_tag_id not in tags:
                sentry_ctx["tag_id"] = AmoCRM.dev_booking_tag_id
                await send_sentry_log(
                    tag="webhook wrapper",
                    message="miss accepted tag in dev environment",
                    context=sentry_ctx,
                )
                return None
        elif maintenance_settings["environment"] == EnvTypes.STAGE:
            if AmoCRM.stage_booking_tag_id not in tags:
                sentry_ctx["tag_id"] = AmoCRM.stage_booking_tag_id
                await send_sentry_log(
                    tag="webhook wrapper",
                    message="miss accepted tag in stage environment",
                    context=sentry_ctx,
                )
                return None
        elif maintenance_settings["environment"] == EnvTypes.PROD:
            if AmoCRM.dev_booking_tag_id in tags or AmoCRM.stage_booking_tag_id in tags:
                sentry_ctx["tag_ids"] = [AmoCRM.dev_booking_tag_id, AmoCRM.stage_booking_tag_id]
                await send_sentry_log(
                    tag="webhook wrapper",
                    message="miss accepted tag in prod environment",
                    context=sentry_ctx,
                )
                return None
        try:
            return await amocrm_webhook(request, *args, **kwargs)
        except Exception as exc:
            traceback.print_exc()
            sentry_sdk.capture_exception(exc)
            return

    return wrapper
