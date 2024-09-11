from dataclasses import dataclass
from functools import wraps
from typing import Any, Awaitable, Callable, Protocol, Self

from pydantic import BaseModel

from src.core.types import P, RetType
from src.exceptions import InternalError


def default_method_key_builder(func: Callable[..., Any] | None, *args: Any, **kwargs: Any) -> str:
    return "[{modname}]:[{funcname}]:[{args}]:[{kwargs}]".format(
        modname=func.__module__ or "" if func else "",
        funcname=func.__name__ if func else "",
        args=str(args),
        kwargs=sorted(kwargs.items()),
    )


def default_key_builder(*args: Any, **kwargs: Any) -> str:
    return "[{args}]:[{kwargs}]".format(
        args=str(args),
        kwargs=sorted(kwargs.items()),
    )


@dataclass
class CacheStatistics:
    profiling: dict[str, int | float]  # TODO: [low] profiling is not implemented
    hits: int
    total: int
    hit_ratio: float

    def refresh(self) -> None:
        self.hit_ratio = self.hits / self.total if self.total else 0

    @classmethod
    def empty(cls) -> Self:
        return cls(
            profiling={},
            hits=0,
            total=0,
            hit_ratio=0,
        )


class CacheSettings(BaseModel):
    ttl: float
    max_size: int


class CacherProto(Protocol):
    def get_statistics(self) -> CacheStatistics: ...

    async def invalidate_key(self, key: str) -> None: ...

    async def invalidate(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> None: ...

    def cached_func(
        self,
        func: Callable[P, Awaitable[RetType]],
        noself: bool,
        ttl: int | None = None,
        key_builder: Callable[..., str] = default_method_key_builder,
    ) -> Callable[P, Awaitable[RetType]]: ...

    def cached_multi_func(
        self,
        keys_kwarg: str,
        func: Callable[P, Awaitable[RetType]],
        ttl: int | None,
        noself: bool,
        key_builder: Callable[..., str] = default_method_key_builder,
    ) -> Callable[P, Awaitable[RetType]]: ...


def cached_method(
    ttl: int | None = None,
    keys_kwarg: str | None = None,
    single_key_tpl_name: str | None = None,
    key_tpl: str | None = None,
    noself: bool = True,
    cacher_location: str = "cacher",
) -> Callable[[Callable[P, Awaitable[RetType]]], Callable[P, Awaitable[RetType]]]:
    """Generate cached version of method

    Args:
        ttl (int): ttl in seconds
        keys_kwarg(str, optional): name of kwarg that contains list of keys for multi_cached
        single_key_tpl_name (str, optional): name of key that will be passed to key_tpl for multi_cached
        key_tpl (str, optional): string template for generating cache key. Defaults to None.
        noself (bool, optional): Use self for cache key calculation. Defaults to True.

        cacher_location (str, optional):
            Attribute name in which Cacher is saved in class instance. Defaults to "_cacher".

    Returns:
        Callable[[Callable[P, Awaitable[RetType]]], Callable[P, Awaitable[RetType]]]:
            Cached function with same signature
    """

    def wrapper(func: Callable[P, Awaitable[RetType]]) -> Callable[P, Awaitable[RetType]]:
        cached_func_name = f"__cached_{func.__name__}"

        @wraps(func)
        async def _inner(*args: P.args, **kwargs: P.kwargs) -> RetType:
            self = args[0]

            cacher: CacherProto | None = getattr(self, cacher_location, None)
            if not cacher:
                raise InternalError(f"Cacher instance was not found in location {cacher_location}")

            key_builder = _select_key_builder(
                key_tpl=key_tpl,
                keys_kwarg=keys_kwarg,
                single_key_tpl_name=single_key_tpl_name,
            )

            cached_func: Callable[P, Awaitable[RetType]] | None
            if not (cached_func := getattr(self, cached_func_name, None)):
                decorator_kwargs: dict[str, Any] = {
                    "func": func,
                    "ttl": ttl,
                    "noself": noself,
                    "key_builder": key_builder,
                }

                if keys_kwarg:
                    decorator_kwargs["keys_kwarg"] = keys_kwarg

                strategy = cacher.cached_multi_func if keys_kwarg else cacher.cached_func
                cached_func = strategy(**decorator_kwargs)
                setattr(self, cached_func_name, cached_func)

            return await cached_func(*args, **kwargs)

        return _inner

    return wrapper


def _make_default_key_builder_multi(key_tpl: str, single_key_tpl_name: str | None) -> Callable[..., str]:
    def key_builder(key: str, f: Callable[..., Any], *args: Any, **kwargs: Any) -> str:
        kwargs.update({single_key_tpl_name or "key": key})
        return key_tpl.format(**kwargs, key=key)

    return key_builder


def _make_default_key_builder_single(key_tpl: str) -> Callable[..., str]:
    def key_builder(f: Callable[..., Any], *args: Any, **kwargs: Any) -> str:
        return key_tpl.format(**kwargs)

    return key_builder


def _select_key_builder(
    key_tpl: str | None,
    keys_kwarg: str | None,
    single_key_tpl_name: str | None,
) -> Callable[..., str]:
    if keys_kwarg:
        if not key_tpl:
            raise ValueError("If keys_kwarg is set, key_tpl must be set too")

        key_builder = _make_default_key_builder_multi(key_tpl, single_key_tpl_name)

    elif key_tpl:
        key_builder = _make_default_key_builder_single(key_tpl)

    else:
        key_builder = default_method_key_builder

    return key_builder
