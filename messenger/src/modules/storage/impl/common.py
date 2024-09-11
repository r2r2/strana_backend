from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.http.serializers.common import SportResponse
from src.entities.users import Language
from src.modules.storage.interface import CommonOperationsProtocol
from src.modules.storage.models import Sport
from src.providers.i18n import get_localized_column


class CommonOperations(CommonOperationsProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_sports(self, lang: Language) -> list[SportResponse]:
        query = select(
            Sport.id,
            get_localized_column(Sport, "name", lang).label("name"),
        ).order_by(Sport.id)
        result = await self.session.execute(query)
        return [
            SportResponse(
                id=row["id"],
                name=row["name"],
            )
            for row in result.mappings()
        ]
