import structlog
from http import HTTPStatus

from fastapi import APIRouter, Path, Request
from starlette.requests import ClientDisconnect

from common.amocrm import AmoCRM
from common.amocrm.decorators import handle_amocrm_webhook_errors
from config import amocrm_config
from .decorators import amocrm_contact_webhook_maintenance
from src.users.use_cases.amocrm_contact_webhook import AmoCRMContactWebhookCase
from ...repos import UserRepo, UserRoleRepo
from ...services import ImportContactFromAmoService

amocrm_contact_router = APIRouter(
    prefix="/amocrm_contact",
    tags=["Amocrm Contact WebHook"]
)


@amocrm_contact_router.post("/update/{client_secret}", status_code=HTTPStatus.OK)
@amocrm_contact_webhook_maintenance
@handle_amocrm_webhook_errors
async def amocrm_contact_webhook(
        request: Request,
        client_secret: str = Path(...)
):
    try:
        payload: bytes = await request.body()
    except ClientDisconnect:
        payload: bytes = bytes()
        client_secret: str = "wrong_secret"

    amocrm_contact_webhook_enabled = request.app.unleash.is_enabled(request.app.feature_flags.amocrm_contact_webhook)
    if amocrm_contact_webhook_enabled:
        logger = structlog.getLogger("amocrm_contact_webhook")
        logger.info("AMOcrm webhook payload", payload=payload)

    await _amocrm_contact_webhook(payload, client_secret)


async def _amocrm_contact_webhook(payload: bytes, client_secret: str) -> None:
    contact_service = ImportContactFromAmoService(
        amocrm_class=AmoCRM,
        user_repo=UserRepo,
        user_role_repo=UserRoleRepo,
    )
    amocrm_contact_webhook_uc = AmoCRMContactWebhookCase(
        amocrm_config=amocrm_config,
        import_contact_service=contact_service
    )
    await amocrm_contact_webhook_uc(payload, client_secret)
