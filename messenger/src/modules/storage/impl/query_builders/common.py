from typing import Any

from sqlalchemy import Select, literal, select
from sqlalchemy import func as sqla_func
from sqlalchemy.ext.asyncio import AsyncSession


async def get_count(query: Select[Any], sess: AsyncSession) -> int:
    count_subq = select(sqla_func.count()).select_from(
        query.with_only_columns(literal("1")).limit(None).offset(None).subquery(),
    )
    return (await sess.execute(count_subq)).scalar() or 0
