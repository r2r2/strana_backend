from contextlib import asynccontextmanager
from time import perf_counter
from typing import Any, AsyncGenerator

from sqlalchemy.engine import Connection, ExecutionContext
from sqlalchemy.event import listens_for
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine

from src.core.logger import get_logger
from src.modules.storage.settings import DatabaseSettings


def add_profiling_hooks(engine: AsyncEngine, time_threshold: float) -> None:
    logger = get_logger("profiling")

    @listens_for(engine.sync_engine, "before_cursor_execute")
    def before_execute(
        conn: Connection,
        cursor: Any,
        statement: str,
        parameters: tuple[str, ...],
        context: ExecutionContext,
        executemany: bool,
    ) -> None:
        context._query_start_time = perf_counter()  # type: ignore

    @listens_for(engine.sync_engine, "after_cursor_execute")
    def after_execute(
        conn: Connection,
        cursor: Any,
        statement: str,
        parameters: tuple[str, ...],
        context: ExecutionContext,
        executemany: bool,
    ) -> None:
        total = perf_counter() - context._query_start_time  # type: ignore
        if total > time_threshold:
            logger.warning(
                "Query to the database is too slow",
                total=total,
                query=statement,
                bind_params=str(parameters),
            )


def create_engine(settings: "DatabaseSettings") -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    engine = _create_async_engine(
        settings.dsn_async,
        echo=settings.echo,
        pool_size=settings.pool_size,
        max_overflow=settings.max_overflow,
        connect_args={"timeout": settings.timeout},
        future=True,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    if settings.is_profiling_enabled:
        add_profiling_hooks(engine, settings.slow_query_time_threshold)

    return engine, session_factory


@asynccontextmanager
async def create_session(session_factory: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


@asynccontextmanager
async def autocommit_session(session_factory: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        await session.connection(execution_options={"isolation_level": "AUTOCOMMIT"})
        yield session
