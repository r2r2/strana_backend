from datetime import date

from fastapi import Depends

from src.api.http.serializers.statistics import TicketsStatisticsResponse
from src.entities.users import Ability, AuthPayload
from src.exceptions import NotPermittedError
from src.modules.storage.dependencies import inject_storage
from src.modules.storage.interface import StorageProtocol
from src.providers.time import end_of_day, start_of_day


class StatisticsController:
    def __init__(
        self,
        storage: StorageProtocol = Depends(inject_storage),
    ) -> None:
        self._storage = storage

    async def get_tickets_statistics(
        self,
        user: AuthPayload,
        for_user_id: int | None,
        date_from: date,
        date_to: date,
    ) -> TicketsStatisticsResponse:
        match for_user_id:
            case None if user.has_ability(Ability.EXTENDED_STATISTICS):
                for_user = None
            case None if not user.has_ability(Ability.EXTENDED_STATISTICS):
                for_user = user.id
            case value:
                if value != user.id and not user.has_ability(Ability.EXTENDED_STATISTICS):
                    raise NotPermittedError("You can't get statistics for other users")

                for_user = value

        result = await self._storage.statistics.get_ticket_stats(
            for_user=for_user,
            date_from=start_of_day(date_from),
            date_to=end_of_day(date_to),
        )

        returned_tickets_percent = 0.0
        if result.solved_tickets_count:
            returned_tickets_percent = result.returned_tickets_count / result.solved_tickets_count

        return TicketsStatisticsResponse(
            **result.dict(),
            returned_tickets_percent=returned_tickets_percent,
        )
