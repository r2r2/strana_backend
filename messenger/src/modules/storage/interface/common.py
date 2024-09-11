from typing import Protocol

from src.api.http.serializers.common import SportResponse
from src.entities.users import Language


class CommonOperationsProtocol(Protocol):
    async def get_sports(self, lang: Language) -> list[SportResponse]: ...
