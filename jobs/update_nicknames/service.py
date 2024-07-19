import re

from sqlalchemy.ext.asyncio import AsyncSession
from structlog.typing import FilteringBoundLogger

from jobs.update_nicknames.dao import CyberPlayerInfo, ImplanDAO, LocalDAO

_sl_title_regex = re.compile(r"(?P<team_name>.+) \((?P<nickname>.+)\)")


class UpdateNicknameService:
    def __init__(
        self,
        session: AsyncSession,
        sl_session: AsyncSession,
        logger: FilteringBoundLogger,
    ):
        self._local_dao = LocalDAO(session)
        self._implan_dao = ImplanDAO(sl_session)
        self._logger = logger

    async def update(self) -> None:
        await self._local_dao.delete_duplicates()

        sl_teams_map = {player_info.sl_id: player_info for player_info in await self._local_dao.get_sl_ids_for_cybers()}

        players_to_update = []

        for team_info in await self._implan_dao.get_teams(sl_teams_map.keys()):
            title_en_match = _sl_title_regex.match(team_info.title_en)
            if title_en_match:
                sl_nickname = title_en_match.group("nickname")
            else:
                sl_nickname = team_info.title_en

            local_player_nickname = sl_teams_map[team_info.id].nickname

            if local_player_nickname == sl_nickname:
                continue

            local_player_id = sl_teams_map[team_info.id].player_id

            players_to_update.append(
                CyberPlayerInfo(
                    id=local_player_id,
                    nickname=sl_nickname,
                    short_name_ru=sl_nickname,
                    short_name_en=sl_nickname,
                    search_field=f"{local_player_id}||{sl_nickname}",
                )
            )

        if players_to_update:
            await self._local_dao.update_cyber_player_nicknames(players_to_update)

        self._logger.info(f"Кол-во обновленных никнеймов игроков: {len(players_to_update)}")
