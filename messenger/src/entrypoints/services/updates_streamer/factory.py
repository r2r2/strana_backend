from src.api.ws.updates_streamer import updates_streamer_router
from src.core.di import setup_dependencies
from src.core.factory import AppFactory, AppWithState, HealthCheckable
from src.core.logger import get_logger
from src.core.settings import load_settings
from src.entrypoints.services.updates_streamer.settings import UpdatesStreamerServiceSettings
from src.entrypoints.services.updates_streamer.state import UpdatesStreamerState
from src.modules.auth import AuthServiceProto
from src.modules.auth.service import AuthService
from src.modules.storage import StorageServiceProto
from src.modules.storage.service import StorageService
from src.modules.updates_streamer.connections import StreamerConnManager
from src.modules.updates_streamer.interface import StreamerConnServiceProto

UpdatesStreamerApp = AppWithState[UpdatesStreamerState]


class UpdatesStreamerFactory(AppFactory[UpdatesStreamerState, UpdatesStreamerServiceSettings]):
    def create_app(self) -> UpdatesStreamerApp:
        settings = load_settings(UpdatesStreamerServiceSettings)
        app = self.create_base_app(settings)
        app.include_router(updates_streamer_router)
        return self._setup_state(app, settings)

    def health_check(self, app: UpdatesStreamerApp) -> list[HealthCheckable]:
        context = app.state
        return [
            HealthCheckable("auth", context.auth.health_check()),
            HealthCheckable("storage", context.storage.health_check()),
        ]

    def _setup_state(self, app: UpdatesStreamerApp, settings: UpdatesStreamerServiceSettings) -> UpdatesStreamerApp:
        storage = StorageService(settings=settings.storage.db)
        auth = AuthService(settings=settings.auth)
        conn_service = StreamerConnManager()

        app.state = UpdatesStreamerState(
            state={
                "auth": auth,
                "storage": storage,
                "connections": conn_service,
            },
        )

        setup_dependencies(
            app,
            settings,
            deps={
                AuthServiceProto: auth,
                StorageServiceProto: storage,
                StreamerConnServiceProto: conn_service,
            },
        )

        return app

    async def on_startup(self, app: UpdatesStreamerApp) -> None:
        await super().on_startup(app)
        await app.state.auth.start()
        await app.state.storage.start()
        self.logger.debug("App started")

    async def on_shutdown(self, app: UpdatesStreamerApp) -> None:
        await super().on_shutdown(app)
        await app.state.storage.stop()
        await app.state.auth.stop()
        self.logger.debug("App stopped")


def entrypoint() -> UpdatesStreamerApp:
    factory = UpdatesStreamerFactory(get_logger())
    return factory.create_app()
