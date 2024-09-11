# type: ignore

from alembic import context
from sqlalchemy import engine_from_config, pool

from src.modules.storage.models import *  # noqa: F403
from src.modules.storage.models.base import Base

target_metadata = Base.metadata


def run_migrations() -> None:
    connectable = engine_from_config(
        context.config.config_args,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.begin() as connection:
        schema_name = context.config.get_main_option("schema_name", False)

        if context.config.get_main_option("create_schema_on_migration", False):
            connection.exec_driver_sql(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            version_table_schema=schema_name,
            version_table=f"{schema_name}_alembic_version",
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations()
