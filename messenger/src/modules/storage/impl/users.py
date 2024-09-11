from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.constants import INT32_MAX
from src.core.types import UserId
from src.entities.users import Role
from src.modules.storage.impl.query_builders.common import get_count
from src.modules.storage.interface import UserOperationsProtocol
from src.modules.storage.models.user import User
from src.providers.time import datetime_now


class UserOperations(UserOperationsProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def search(
        self,
        exclude_user_id: int | None = None,
        search_string: str | None = None,
        filter_by_role: Role | None = None,
        limit: int | None = None,
        offset: int | None = None,
        exclude_roles: list[Role] | None = None,
    ) -> tuple[list[User], int]:
        query = select(User).limit(limit).offset(offset)

        if exclude_roles:
            query = query.where(User.role.not_in(exclude_roles))

        if filter_by_role:
            query = query.where(User.role == filter_by_role)

        if exclude_user_id:
            query = query.where(User.sportlevel_id != exclude_user_id)

        if search_string:
            search_string = search_string.lower()

            if search_string.isdigit() and search_string.isascii():
                search_val = int(search_string)
                if search_val < INT32_MAX:
                    query = query.where(
                        or_(
                            User.sportlevel_id == search_val,
                            User.scout_number == search_val,
                        ),
                    )
            else:
                query = query.where(func.lower(User.name).contains(search_string))

        result = await self.session.execute(query)
        count = await get_count(query, self.session)
        return list(result.scalars().all()), count

    async def get_by_id(self, user_id: UserId) -> User | None:
        query = select(User).where(User.sportlevel_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_ids(self, user_ids: list[UserId]) -> list[User]:
        query = select(User).where(User.sportlevel_id.in_(user_ids))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(
        self,
        user_id: UserId,
        name: str,
        scout_number: int | None,
        role: Role,
    ) -> None:
        user = User(
            sportlevel_id=user_id,
            name=name,
            scout_number=scout_number,
            role=role,
            created_at=datetime_now(),
            updated_at=None,
        )
        self.session.add(user)
        await self.session.flush()

    async def update(
        self,
        user_id: int,
        name: str,
        scout_number: int | None,
        role: Role | None = None,
    ) -> None:
        updates = {
            "name": name,
            "scout_number": scout_number,
            "updated_at": datetime_now(),
        }
        if role:
            updates["role"] = role

        query = update(User).values(**updates).where(User.sportlevel_id == user_id)
        await self.session.execute(query)

    async def update_role(self, role: Role, user_id: UserId) -> None:
        query = update(User).values(role=role, updated_at=datetime_now()).where(User.sportlevel_id == user_id)
        await self.session.execute(query)
