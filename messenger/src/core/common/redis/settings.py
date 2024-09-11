from pydantic import BaseModel, SecretStr


class RedisSettings(BaseModel):
    host: str
    port: int
    debug: bool = False
    db: str | int
    max_connections: int
    reconnect_max_retries: int
    username: str | None
    password: SecretStr | None
    is_profiling_enabled: bool = False
    slow_query_time_threshold: float = 0.005
