from datetime import datetime
from typing import AsyncGenerator

from sl_api_client import SlAPIClient
from sl_api_client.serializers.matches import MatchResponse
from sl_api_client.serializers.users import UpdateUserRequest, UserResponse

from src.core.logger import LoggerName, get_logger
from src.entities.matches import MatchDataWithState, MatchScoutData, MatchTeamData
from src.entities.users import Language
from src.modules.sportlevel.helpers import clean_scout_name
from src.modules.sportlevel.interface import SLMatchState, SportlevelServiceProto
from src.modules.sportlevel.settings import SportlevelSettings


class SportlevelService(SportlevelServiceProto):
    def __init__(self, settings: SportlevelSettings) -> None:
        self.logger = get_logger(LoggerName.SL)
        self.settings = settings
        self._client = SlAPIClient(
            logger=self.logger.bind(subtype="client"),
            settings=settings,
        )

    def sl_response_to_match_data(self, response: MatchResponse) -> MatchDataWithState | None:
        if not response.team_a or not response.team_b or not response.start_at or not response.state_id:
            return None

        return MatchDataWithState(
            state=SLMatchState(response.state_id).to_match_state(),
            sportlevel_id=response.id,
            start_at=response.start_at,
            finish_at=response.finish_at,
            sport_id=response.sport_id,
            team_a=MatchTeamData(
                id=response.team_a.id,
                name_ru=response.team_a.title_ru or "Не указана",
                name_en=response.team_a.title_en or "TBD",
            ),
            team_b=MatchTeamData(
                id=response.team_b.id,
                name_ru=response.team_b.title_ru or "Не указана",
                name_en=response.team_b.title_en or "TBD",
            ),
            scouts=[
                MatchScoutData(
                    scout_number=scout.scout_num,
                    is_main_scout=scout.is_main,
                    name=clean_scout_name(scout.name),
                    id=scout.id,
                )
                for scout in (response.scouts or [])
                if scout.scout_num is not None
            ],
        )

    async def start(self) -> None:
        await self._client.setup()
        # await self._client._http_client.renew_api_token()
        self.logger.debug("Authorized in the sportlevel API")

    async def stop(self) -> None:
        await self._client.cleanup()

    async def health_check(self) -> bool:
        return True
        # return await self._client.healthcheck() TODO: fix health check

    async def change_language(self, user_id: int, lang: Language) -> bool:
        try:
            await self._client.users.update(
                user_id=user_id,
                payload=UpdateUserRequest(lang=lang.value),
            )
            return True
        except Exception:
            self.logger.warning("Cannot update lang for user", user_id=user_id, exc_info=True)
            return False

    async def get_match_by_id(self, match_id: int) -> MatchDataWithState | None:
        response = await self._client.matches.get_by_id(match_id=match_id)
        return self.sl_response_to_match_data(response)

    async def get_user_by_id(self, user_id: int) -> UserResponse | None:
        try:
            return await self._client.users.get_by_id(user_id=user_id)

        except Exception:
            self.logger.warning("Cannot get user by id", user_id=user_id, exc_info=True)
            return None

    async def iter_matches(
        self,
        date_from: datetime,
        date_to: datetime,
        state_id: int | None = None,
    ) -> AsyncGenerator[MatchDataWithState, None]:
        async for match_info in self._client.matches.iter_search(
            start_from=date_from,
            start_to=date_to,
            state_id=state_id,
        ):
            converted = self.sl_response_to_match_data(match_info)
            if converted:
                yield converted
