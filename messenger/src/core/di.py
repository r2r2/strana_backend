from typing import Any, Callable, Type, TypeVar, cast

from fastapi import Depends as FastAPIDepends
from fastapi import FastAPI
from pydantic import BaseModel

from src.core.settings import BaseServiceSettings
from src.core.types import T

WrappedType = TypeVar("WrappedType")


class _WrapperInner:
    def __init__(self, key: Any) -> None:
        self.key = key

    def __eq__(self, __o: Any) -> bool:
        if isinstance(__o, type(self)):
            return cast(bool, self.key == __o.key)

        return False

    def __hash__(self) -> int:
        return hash(self.key)

    def __call__(self) -> Any:
        dep_name = getattr(self.key, "__name__", str(self.key))
        raise NotImplementedError(f"Dependency is not injected: {dep_name}")


class Injector:
    """
    Simple wrapper around `fastapi.Depends`

    Problem and considerations: https://github.com/tiangolo/fastapi/issues/4118

    Usage example::

        import typing
        from fastapi import FastAPI
        from src.core.di import Inject, setup_dependencies

        class SomeInterface(typing.Protocol): ...

        class ConcreteImpl: ...

        app = FastAPI()

        @app.get("")
        def my_api_route(
            module: SomeInterface = Inject[SomeInterface],
        ) -> None:
            ...

        module = ConcreteImpl()
        setup_dependencies(
            app,
            settings,
            deps={
                SomeInterface: module,
            },
            as_callables: True,
            # or:
            # deps={
            #     SomeInterface: lambda: module,
            # },
            # as_callables: False,
        )

    """

    def __getitem__(self, key: Type[WrappedType]) -> WrappedType:
        return FastAPIDepends(_WrapperInner(key))


def _as_callable(obj: T) -> Callable[[], T]:
    def _inner():
        return obj

    return _inner


def setup_dependencies(
    app: FastAPI,
    settings: BaseServiceSettings,
    deps: dict[Any, Any],
    as_callables: bool = True,
) -> None:
    """
    The function is used to set up dependencies for a FastAPI application.
    It updates dependency_overrides with provided `deps` value,
    and additionally adds all sections from the settings to dependencies.

    Usage example::

        setup_dependencies(
            app,
            settings=settings,
            deps={
                ModuleProto: module
            },
            as_callables: True
        )

        # app.dependency_overrides == {
        #     ModuleProto: lambda: module,
        #     SettingsSection: lambda: settings.section
        # }
    """
    sections_with_classes = {
        type(settings_section): settings_section
        for _, settings_section in settings
        if isinstance(settings_section, BaseModel)
    }
    deps[type(settings)] = settings
    deps.update(sections_with_classes)

    if as_callables:
        overrides = {_WrapperInner(key): _as_callable(value) for key, value in deps.items()}
    else:
        overrides = {_WrapperInner(key): value for key, value in deps.items()}

    app.dependency_overrides.update(overrides)  # type: ignore


Injected = Injector()


__all__ = ("Injected", "setup_dependencies")
