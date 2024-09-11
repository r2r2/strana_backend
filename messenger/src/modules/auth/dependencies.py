from typing import Annotated, Awaitable, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.di import Injected
from src.entities.users import Ability, AuthPayload, Role
from src.exceptions import AuthRequiredError, InvalidAuthCredentialsError
from src.modules.auth import AuthServiceProto
from src.modules.auth.settings import AuthSettings

sl_auth_bearer = HTTPBearer(
    auto_error=False,
    description="JWT token emitted by the `SL Auth` service",
)


class AuthOptional:
    def __init__(self, use_extended_leeway: bool = False) -> None:
        self._use_extended_leeway = use_extended_leeway

    async def __call__(
        self,
        header_auth: HTTPAuthorizationCredentials | None = Depends(sl_auth_bearer),
        settings: AuthSettings = Injected[AuthSettings],
        auth_service: AuthServiceProto = Injected[AuthServiceProto],
    ) -> AuthPayload | None:
        if not header_auth:
            return None

        if self._use_extended_leeway:
            leeway = settings.extended_token_leeway or settings.token_leeway
        else:
            leeway = settings.token_leeway

        try:
            user_info = await auth_service.process_credentials(header_auth.credentials, leeway=leeway)

        except AuthRequiredError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=exc.message,
            ) from exc

        except InvalidAuthCredentialsError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message) from exc

        if not user_info.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to access this resource",
            )

        return user_info


auth_optional = AuthOptional()


async def auth_required(
    auth: AuthPayload | None = Depends(auth_optional),
) -> AuthPayload:
    if not auth:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You are not allowed to access this resource")

    return auth


def role_required(*roles: Role) -> Callable[[AuthPayload], Awaitable[AuthPayload]]:
    async def _inner(user: AuthPayload = Depends(auth_required)) -> AuthPayload:
        if not any(role in user.roles for role in roles):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"This action requires one of the roles: {[role.value for role in roles]}",
            )

        return user

    return _inner


def ability_required(*abilities: Ability) -> Callable[[AuthPayload], Awaitable[AuthPayload]]:
    async def _inner(user: AuthPayload = Depends(auth_required)) -> AuthPayload:
        if not any(ability in user.abilities for ability in abilities):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"This action requires one of the abilities: {[ability.value for ability in abilities]}",
            )

        return user

    return _inner


UserAuth = Annotated[AuthPayload, Depends(auth_required)]

supervisor_required = role_required(Role.SUPERVISOR)
bookmaker_required = role_required(Role.BOOKMAKER)
admin_required = ability_required(Ability.ADMIN)

__all__ = ("UserAuth", "admin_required", "auth_required", "supervisor_required", "bookmaker_required")
