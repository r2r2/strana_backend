from sqlalchemy import delete, distinct, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.common.utility import exclude_fields
from src.core.types import UserId
from src.entities.matches import (
    ChatType,
    MatchDataWithState,
    MatchFilters,
    MatchScoutData,
    MatchState,
    MatchStoredData,
    MatchTeamData,
    MatchUpdatableFields,
)
from src.entities.users import Language, Role
from src.modules.storage.impl.query_builders import MatchesQueryBuilder
from src.modules.storage.interface import MatchOperationsProtocol
from src.modules.storage.models import Chat, ChatMembership, Match, MatchScout, User
from src.providers.i18n import parse_message_content
from src.providers.time import datetime_now


class MatchOperations(MatchOperationsProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def update_match(self, sportlevel_id: int, updates: MatchUpdatableFields) -> None:
        query = (
            update(Match)
            .values(
                updated_at=datetime_now(),
                start_at=updates.start_at,
                finish_at=updates.finish_at,
                sport_id=updates.sport_id,
                team_a_id=updates.team_a.id if updates.team_a else None,
                team_a_name_ru=updates.team_a.name_ru if updates.team_a else None,
                team_a_name_en=updates.team_a.name_en if updates.team_a else None,
                team_b_id=updates.team_b.id if updates.team_b else None,
                team_b_name_ru=updates.team_b.name_ru if updates.team_b else None,
                team_b_name_en=updates.team_b.name_en if updates.team_b else None,
            )
            .where(Match.sportlevel_id == sportlevel_id)
        )
        await self.session.execute(query)

    async def update_match_state(self, sportlevel_id: int, state: MatchState) -> None:
        query = (
            update(Match)
            .values(
                updated_at=datetime_now(),
                state=state,
            )
            .where(Match.sportlevel_id == sportlevel_id)
        )
        await self.session.execute(query)

    async def get_match_by_id(self, sportlevel_id: int) -> MatchDataWithState | None:
        query = MatchesQueryBuilder.build_get_match_basic_info(sportlevel_id=sportlevel_id)

        result = (await self.session.execute(query)).tuples().first()
        if not result:
            return None

        match_info, scouts = result[0], result[1]

        return MatchDataWithState(
            state=match_info.state,
            sport_id=match_info.sport_id,
            sportlevel_id=match_info.sportlevel_id,
            start_at=match_info.start_at,
            finish_at=match_info.finish_at,
            team_a=MatchTeamData(
                id=match_info.team_a_id,
                name_en=match_info.team_a_name_en,
                name_ru=match_info.team_a_name_ru,
            ),
            team_b=MatchTeamData(
                id=match_info.team_b_id,
                name_en=match_info.team_b_name_en,
                name_ru=match_info.team_b_name_ru,
            ),
            scouts=[
                MatchScoutData(
                    id=scout["id"],
                    is_main_scout=scout["is_main_scout"],
                    scout_number=scout["scout_number"],
                    name=scout["name"],
                )
                for scout in scouts
            ],
        )

    async def create_match_with_scouts(self, match_data: MatchDataWithState) -> None:
        match = Match(
            state=match_data.state,
            sportlevel_id=match_data.sportlevel_id,
            created_at=datetime_now(),
            updated_at=None,
            start_at=match_data.start_at,
            finish_at=match_data.finish_at,
            sport_id=match_data.sport_id,
            team_a_id=match_data.team_a.id,
            team_a_name_ru=match_data.team_a.name_ru,
            team_a_name_en=match_data.team_a.name_en,
            team_b_id=match_data.team_b.id,
            team_b_name_ru=match_data.team_b.name_ru,
            team_b_name_en=match_data.team_b.name_en,
        )
        self.session.add(match)

        for scout in match_data.scouts:
            match_scout = MatchScout(
                sportlevel_match_id=match.sportlevel_id,
                scout_number=scout.scout_number,
                is_main_scout=scout.is_main_scout,
            )
            self.session.add(match_scout)

        await self.session.flush()

    async def get_match_info(
        self,
        user_id: UserId,
        user_role: Role,
        lang: Language,
        match_id: int,
    ) -> MatchStoredData | None:
        query_builder = MatchesQueryBuilder(
            user_id=user_id,
            lang=lang,
            user_role=user_role,
        )
        query = query_builder.build_get_match_query(match_id=match_id)
        result = (await self.session.execute(query)).one_or_none()
        if not result:
            return None

        return MatchStoredData(
            **exclude_fields(result._mapping, exclude={"last_message_content"}),
            last_message_content=parse_message_content(result.last_message_content),
        )

    async def get_matches(
        self,
        user_id: UserId,
        user_role: Role,
        lang: Language,
        filters: MatchFilters,
        limit: int,
        offset: int,
    ) -> list[MatchStoredData]:
        query_builder = MatchesQueryBuilder(
            user_id=user_id,
            lang=lang,
            user_role=user_role,
            chat_type=ChatType.MATCH,
        )
        query = query_builder.build_get_match_list_query(filters=filters, limit=limit, offset=offset)
        result = await self.session.execute(query)
        return [
            MatchStoredData(
                **exclude_fields(row, exclude={"last_message_content"}),
                last_message_content=parse_message_content(row.last_message_content),
            )
            for row in result.mappings().fetchall()
        ]

    async def get_matches_list(
        self,
        user_id: UserId,
        user_role: Role,
        lang: Language,
        filters: MatchFilters,
        limit: int,
        offset: int,
    ) -> list[MatchStoredData]:
        query_builder = MatchesQueryBuilder(
            user_id=user_id,
            lang=lang,
            user_role=user_role,
        )
        query = query_builder.build_get_match_list_short_info(filters=filters, limit=limit, offset=offset)
        result = await self.session.execute(query)
        return [MatchStoredData(**row) for row in result.mappings().fetchall()]

    async def get_match_scouts(self, match_id: int) -> list[MatchScoutData]:
        query = (
            select(MatchScout, User)
            .select_from(MatchScout)
            .join(User, User.scout_number == MatchScout.scout_number)
            .where(MatchScout.sportlevel_match_id == match_id)
        )
        result = await self.session.execute(query)
        return [
            MatchScoutData(
                id=user.sportlevel_id,
                scout_number=match_scout.scout_number,
                is_main_scout=match_scout.is_main_scout,
                name=user.name,
            )
            for match_scout, user in result.tuples().all()
        ]

    async def get_match_scout(self, match_id: int, scout_id: int) -> MatchScout | None:
        query = (
            select(MatchScout)
            .select_from(MatchScout)
            .join(User, User.scout_number == MatchScout.scout_number)
            .where(MatchScout.sportlevel_match_id == match_id, User.sportlevel_id == scout_id)
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def set_match_scouts(self, match_id: int, scouts: list[MatchScoutData]) -> None:
        delete_q = delete(MatchScout).where(MatchScout.sportlevel_match_id == match_id)
        await self.session.execute(delete_q)

        for scout in scouts:
            match_scout = MatchScout(
                sportlevel_match_id=match_id,
                scout_number=scout.scout_number,
                is_main_scout=scout.is_main_scout,
            )
            self.session.add(match_scout)

        await self.session.flush()

    async def get_all_users_related_to_match(self, match_id: int) -> list[int]:
        query = (
            select(distinct(ChatMembership.user_id))
            .select_from(Match)
            .join(Chat, Chat.match_id == Match.sportlevel_id)
            .join(ChatMembership, ChatMembership.chat_id == Chat.id)
            .where(Match.sportlevel_id == match_id)
        )
        result = await self.session.execute(query)
        return list(result.scalars())

    async def delete_match_with_scouts(self, match_id: int) -> None:
        delete_q = delete(MatchScout).where(MatchScout.sportlevel_match_id == match_id)
        await self.session.execute(delete_q)

        delete_q = delete(Match).where(Match.sportlevel_id == match_id)
        await self.session.execute(delete_q)
