from typing import Protocol

from src.core.common.utility import SupportsHealthCheck, SupportsLifespan
from src.core.types import UserId
from src.entities.users import AuthPayload


class AuthServiceProto(SupportsHealthCheck, SupportsLifespan, Protocol):
    async def process_credentials(self, credentials: str | None, leeway: int | None = None) -> AuthPayload: ...

    async def parse_service_token(self, token: str) -> str | None: ...

    async def grant(self, user_id: UserId, role: str) -> None: ...

    async def revoke(self, user_id: UserId, role: str) -> None: ...
