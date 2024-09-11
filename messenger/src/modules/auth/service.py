from base64 import b64decode
from json import loads as json_loads
from typing import Any

from sl_auth_client import AuthServiceClient
from sl_auth_client.exceptions import TokenError, WrappedError

from src.core.logger import LoggerName, add_to_log_ctx, get_logger
from src.core.types import UserId
from src.entities.users import Ability, AuthPayload, Role
from src.exceptions import AuthRequiredError, InvalidAuthCredentialsError
from src.modules.auth import AuthSettings
from src.modules.auth.interface import AuthServiceProto
from src.modules.auth.serializers import AuthTokenPayload


class AuthService(AuthServiceProto):
    def __init__(self, settings: AuthSettings) -> None:
        self.logger = get_logger(LoggerName.AUTH)
        self._settings = settings
        self._client = AuthServiceClient(
            base_url=settings.host,
            service_name=settings.aud,
            service_key=settings.priv_key.get_secret_value(),
            timeout=settings.request_timeout,
            user_factory=self._extract_payload,
        )

    def _extract_payload(self, payload: dict[str, Any]) -> AuthTokenPayload:
        return AuthTokenPayload(**payload)

    async def health_check(self) -> bool:
        return self._client.healthcheck()

    async def start(self) -> None:
        if self._settings.verify_signature:
            await self._client.setup()

    async def stop(self) -> None:
        await self._client.cleanup()

    async def process_credentials(self, credentials: str | None, leeway: int | None = None) -> AuthPayload:
        if not credentials:
            raise AuthRequiredError()

        if not self._settings.verify_signature:
            try:
                payload = await self._extract_payload_without_verification(credentials)
            except Exception as exc:
                self.logger.warning(f"Invalid auth credentials: {type(exc).__name__}", exc_info=True)
                raise InvalidAuthCredentialsError() from exc

        else:
            try:
                payload = await self._client.parse_user_token(credentials, leeway=leeway)
            except TokenError as exc:
                self.logger.debug(f"Invalid token: {exc}", exc_info=True)
                raise InvalidAuthCredentialsError(message=str(exc)) from exc

        add_to_log_ctx(user_id=payload.user_id)

        if not payload.roles:
            raise InvalidAuthCredentialsError(message="You are not allowed to access this resource")

        result = AuthPayload(
            id=payload.user_id,
            roles=[Role(token) for token in payload.roles if Role.is_compatible(token)],
            abilities=[Ability(token) for token in payload.roles if Ability.is_compatible(token)],
            lang=payload.lang,
        )

        if not result.roles:
            raise InvalidAuthCredentialsError(message="You are not allowed to access this resource")

        return result

    async def parse_service_token(self, token: str) -> str | None:
        if not self._settings.verify_signature:
            return self._parse_jwt_wo_verification(token).get("sub")

        try:
            return await self._client.parse_service_token(token)
        except WrappedError as exc:
            self.logger.error(f"Invalid service token: {exc}", exc_info=True)
            return None

    async def grant(self, user_id: UserId, role: str) -> None:
        await self._client.grant_role(user_id=user_id, role=role)

    async def revoke(self, user_id: UserId, role: str) -> None:
        await self._client.revoke_role(user_id=user_id, role=role)

    async def get_roles(self, user_id: UserId) -> list[Role]:
        return [
            Role(role_str) for role_str in await self._client.get_roles(user_id=user_id) if Role.is_compatible(role_str)
        ]

    def _parse_jwt_wo_verification(self, token: str) -> dict[str, Any]:
        payload_raw = token.split(".", maxsplit=2)[1] + "=="
        return json_loads(b64decode(payload_raw))

    async def _extract_payload_without_verification(self, credentials: str) -> AuthTokenPayload:
        return self._extract_payload(self._parse_jwt_wo_verification(credentials))
