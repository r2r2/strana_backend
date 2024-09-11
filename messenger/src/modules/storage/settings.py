from pydantic import BaseModel, Field


class DatabaseSettings(BaseModel):
    user: str
    password: str
    host: str
    port: int
    database_name: str
    echo: bool
    pool_size: int
    max_overflow: int
    timeout: float
    is_profiling_enabled: bool
    slow_query_time_threshold: float = 0.1

    @property
    def _dsn_without_proto(self) -> str:
        return f"{self.user}:{self.password}@{self.host}:{self.port}/{self.database_name}"

    @property
    def dsn_async(self) -> str:
        return f"postgresql+asyncpg://{self._dsn_without_proto}"

    @property
    def dsn_sync(self) -> str:
        return f"postgresql://{self._dsn_without_proto}"


class MigratorSettings(BaseModel):
    create_schema_on_migration: bool = False
    schema_name: str = "public"


class StorageSettings(BaseModel):
    db: DatabaseSettings
    migrator: MigratorSettings = Field(default_factory=MigratorSettings)
