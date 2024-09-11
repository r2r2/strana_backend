from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import partial
from typing import Awaitable, Generic, TypeVar

from boilerplates.sentry import setup_sentry
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from secret_docs import DocsConfig, install_docs
from sl_healthchecks import CompoundChecker
from sl_healthchecks.compound import apply_checks
from sl_healthchecks.result import CompoundCheckResult
from starlette.datastructures import State
from starlette.middleware import Middleware
from starlette_context.middleware import RawContextMiddleware

from src.core.logger import setup_logging
from src.core.middleware import RequestLoggingMiddleware
from src.core.settings import BaseServiceSettings
from src.core.types import LoggerType

AppStateT = TypeVar("AppStateT", bound=State)
SettingsT = TypeVar("SettingsT", bound=BaseServiceSettings)


@dataclass
class HealthCheckable:
    name: str
    func: Awaitable[bool]


class AppWithState(FastAPI, Generic[AppStateT]):
    state: AppStateT  # type: ignore


class AppFactory(Generic[AppStateT, SettingsT], ABC):
    def __init__(self, logger: LoggerType) -> None:
        self.logger = logger

    @abstractmethod
    def health_check(self, app: AppWithState[AppStateT]) -> list[HealthCheckable]: ...

    @abstractmethod
    def create_app(self) -> AppWithState[AppStateT]: ...

    async def _health_check(self, app: AppWithState[AppStateT]) -> CompoundCheckResult:
        checker = CompoundChecker(wait_in_seconds=3.0)
        checks = [
            checker.create_checker(
                check=rule.func,
                name=rule.name,
            )
            for rule in self.health_check(app)
        ]

        return await apply_checks(*checks)

    def create_base_app(self, settings: BaseServiceSettings) -> AppWithState[AppStateT]:
        setup_logging(
            settings=settings.logging,
            is_sentry_enabled=settings.sentry.is_enabled,
        )
        if settings.sentry.is_enabled:
            setup_sentry(settings.sentry, app_version=settings.app.version)

        app = AppWithState(
            title=settings.app.title,
            version=settings.app.version,
            root_path=settings.app.api_root_path,
            debug=settings.app.debug,
            docs_url=None,
            redoc_url=None,
            openapi_url=None,
            middleware=[
                Middleware(RawContextMiddleware),
                Middleware(RequestLoggingMiddleware),
            ],
        )

        if settings.cors.is_enabled:
            app.add_middleware(
                CORSMiddleware,
                allow_origins=settings.cors.allow_origins,
                allow_credentials=settings.cors.allow_credentials,
                allow_methods=settings.cors.allow_methods,
                allow_headers=settings.cors.allow_headers,
            )

        if settings.docs.is_enabled:
            install_docs(
                app,
                config=DocsConfig(
                    auth_required=True,
                    username=settings.docs.username,
                    password=settings.docs.password.get_secret_value(),
                    version=settings.app.version,
                    title=settings.app.title,
                    public_url="/docs",
                    json_url="/api.json",
                ),
            )

        app.add_event_handler("startup", partial(self.on_startup, app))
        app.add_event_handler("shutdown", partial(self.on_shutdown, app))

        self._add_health_check(app)

        self.logger.debug("Base app created")
        return app

    async def on_startup(self, app: AppWithState[AppStateT]) -> None:  # pylint: disable=unused-argument
        self.logger.debug("App is starting")

    async def on_shutdown(self, app: AppWithState[AppStateT]) -> None:  # pylint: disable=unused-argument
        self.logger.debug("App is shutting down")

    def _add_health_check(self, app: AppWithState[AppStateT]) -> None:
        app.get("/health_check", summary="Healthcheck", tags=["Service management"])(partial(self._health_check, app))
