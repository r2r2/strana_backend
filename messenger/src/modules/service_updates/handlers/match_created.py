from sqlalchemy.exc import IntegrityError

from src.core.types import ConnectionId
from src.modules.service_updates.entities import MatchCreated
from src.modules.service_updates.handlers.base import BaseUpdateHandler


class MatchCreatedUpdateHandler(BaseUpdateHandler[MatchCreated], update_type=MatchCreated):
    async def handle(self, cid: ConnectionId | None, update: MatchCreated) -> None:
        async with self.storage_srvc.connect(autocommit=True) as db:
            if not (_existing_match := await db.matches.get_match_by_id(update.payload.sportlevel_id)):
                try:
                    await db.matches.create_match_with_scouts(update.payload)
                except IntegrityError:
                    self.logger.info(f"Match already exists: {update.payload.sportlevel_id} -> {update.payload}")
                else:
                    self.logger.debug(f"Match created: {update.payload.sportlevel_id} -> {update.payload}")
