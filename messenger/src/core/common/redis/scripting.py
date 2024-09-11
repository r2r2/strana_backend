from src.constants import LUA_SCRIPTS_FOLDER
from src.core.types import RedisConn


class RedisScript:
    source_name: str

    def __init__(self, bind_to: RedisConn) -> None:
        script_path = LUA_SCRIPTS_FOLDER / f"{self.source_name}.lua"

        if not script_path.exists():
            raise FileNotFoundError(f"File {script_path} does not exist")

        self._lua_source = script_path.read_text()
        self._conn = bind_to
        self._script = bind_to.register_script(self._lua_source)


class IncrementManyIfExists(RedisScript):
    source_name = "increment_many_if_exists"

    async def __call__(self, incr_by: int, keys: list[str], conn: "RedisConn | None" = None) -> dict[str, int]:
        if not keys:
            return {}

        conn = conn or self._conn

        script_output = await self._script(args=[incr_by, *keys])

        return {item[0].decode(): item[1] for item in script_output}


class DecrementManyIfExists(RedisScript):
    source_name = "decrement_many_if_exists"

    async def __call__(self, decr_by: int, keys: list[str], conn: "RedisConn | None" = None) -> dict[str, int]:
        if not keys:
            return {}

        conn = conn or self._conn

        script_output = await self._script(args=[decr_by, *keys])

        return {item[0].decode(): item[1] for item in script_output}
