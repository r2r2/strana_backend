from dataclasses import dataclass
from typing import Generic, TypeVar

from cachetools import TTLCache

from src.core.common.caching import CacheSettings
from src.entities.matches import MatchBasicData, MatchDataWithState, MatchScoutData, MatchState

CachedTypeT = TypeVar("CachedTypeT")
CacheKeyT = TypeVar("CacheKeyT")


@dataclass(slots=True, frozen=True, repr=True, eq=True)
class UserCacheData:
    id: int
    name: str
    scout_number: int | None


@dataclass(slots=True, frozen=True, repr=True, eq=True)
class MatchScoutCacheData:
    scout_number: int
    is_main_scout: bool


@dataclass(slots=True, frozen=True, repr=True, eq=True)
class MatchCacheData:
    fields: MatchBasicData
    scouts: list[MatchScoutCacheData]
    state: MatchState

    def is_scouts_changed(self, scouts: list[MatchScoutData]) -> bool:
        return self.scouts != [
            MatchScoutCacheData(scout_number=scout.scout_number, is_main_scout=scout.is_main_scout) for scout in scouts
        ]

    def is_fields_changed(self, fields: MatchDataWithState) -> bool:
        return self.fields != fields.to_basic_fields()


class SLSyncInMemoryCache(Generic[CacheKeyT, CachedTypeT]):
    def __init__(self, cfg: CacheSettings) -> None:
        self._cache = TTLCache[CacheKeyT, CachedTypeT](maxsize=cfg.max_size, ttl=cfg.ttl)

    def get(self, key: CacheKeyT) -> CachedTypeT | None:
        return self._cache.get(key)

    def update(self, key: CacheKeyT, data: CachedTypeT) -> None:
        self._cache[key] = data
