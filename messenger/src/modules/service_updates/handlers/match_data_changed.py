from src.core.types import ConnectionId
from src.entities.matches import MatchUpdatableFields
from src.modules.service_updates.entities import MatchDataChanged
from src.modules.service_updates.handlers.base import BaseUpdateHandler


class MatchDataChangedUpdateHandler(BaseUpdateHandler[MatchDataChanged], update_type=MatchDataChanged):
    async def handle(self, cid: ConnectionId | None, update: MatchDataChanged) -> None:
        async with self.storage_srvc.connect(autocommit=True) as db:
            await db.matches.update_match(
                sportlevel_id=update.sportlevel_id,
                updates=MatchUpdatableFields(
                    start_at=update.fields.start_at,
                    sport_id=update.fields.sport_id,
                    finish_at=update.fields.finish_at,
                    team_a=update.fields.team_a,
                    team_b=update.fields.team_b,
                ),
            )
            self.logger.debug(f"Match updated: {update.sportlevel_id} -> {update.fields}")
