from fastapi import APIRouter, Depends

from src.api.http.serializers.common import ChangeLanguageRequest, SportResponse
from src.core.di import Injected
from src.core.logger import LoggerName, get_logger
from src.entities.reactions import EmojiEnum
from src.entities.users import AuthPayload
from src.modules.auth.dependencies import auth_required
from src.modules.sportlevel import SportlevelServiceProto
from src.modules.storage.dependencies import StorageProtocol, inject_storage

common_router = APIRouter(prefix="/common")


@common_router.get(
    "/sports",
    summary="Get sports",
)
async def get_sports(
    storage: StorageProtocol = Depends(inject_storage),
    user: AuthPayload = Depends(auth_required),
) -> list[SportResponse]:
    return await storage.common.get_sports(lang=user.lang)


@common_router.post(
    "/language",
    summary="Change language",
)
async def change_language(
    request: ChangeLanguageRequest,
    sportlevel_service: SportlevelServiceProto = Injected[SportlevelServiceProto],
    user: AuthPayload = Depends(auth_required),
) -> None:
    try:
        await sportlevel_service.change_language(user_id=user.id, lang=request.lang)
    except Exception as exc:
        get_logger(LoggerName.SL).exception(
            f"Error while changing language for user {user.id}: {exc}",
        )


@common_router.get(
    "/emojis",
    summary="Get emojis",
)
async def get_emojis(_: AuthPayload = Depends(auth_required)) -> dict[str, str]:
    return {k: v.value for k, v in EmojiEnum.__members__.items()}
