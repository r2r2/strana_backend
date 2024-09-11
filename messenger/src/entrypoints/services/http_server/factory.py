from src.api.http.router import http_api_router
from src.core.common.rabbitmq import RabbitMQPublisherFactory, RabbitMQPublisherFactoryProto
from src.core.di import setup_dependencies
from src.core.factory import AppFactory, AppWithState, HealthCheckable
from src.core.logger import get_logger
from src.core.settings import load_settings
from src.entrypoints.services.http_server.settings import HTTPServiceSettings
from src.entrypoints.services.http_server.state import HTTPServiceState
from src.modules.auth import AuthServiceProto
from src.modules.auth.service import AuthService
from src.modules.presence import PresenceServiceProto
from src.modules.presence.service import PresenceService
from src.modules.sportlevel import SportlevelServiceProto
from src.modules.sportlevel.service import SportlevelService
from src.modules.storage import StorageServiceProto
from src.modules.storage.service import StorageService
from src.modules.users_cache import UsersCacheProtocol
from src.modules.users_cache.service import UsersCacheService

HTTPServiceApp = AppWithState[HTTPServiceState]


class HTTPServiceFactory(AppFactory[HTTPServiceState, HTTPServiceSettings]):
    def create_app(self) -> HTTPServiceApp:
        settings = load_settings(HTTPServiceSettings)
        app = self.create_base_app(settings)
        app.include_router(http_api_router)
        return self._setup_state(app, settings)

    def health_check(self, app: HTTPServiceApp) -> list[HealthCheckable]:
        context = app.state
        return [
            HealthCheckable("auth", context.auth.health_check()),
            HealthCheckable("rabbitmq_publisher", context.rabbitmq_publisher.health_check()),
            HealthCheckable("storage", context.storage.health_check()),
            HealthCheckable("sportlevel", context.sportlevel.health_check()),
            HealthCheckable("presence", context.presence.health_check()),
        ]

    def _setup_state(self, app: HTTPServiceApp, settings: HTTPServiceSettings) -> HTTPServiceApp:
        storage = StorageService(settings=settings.storage.db)

        rabbitmq_publisher = RabbitMQPublisherFactory(settings.rabbitmq_publisher.amqp)

        presence_srvc = PresenceService(settings=settings.presence)

        auth = AuthService(settings=settings.auth)

        sportlevel = SportlevelService(settings=settings.sportlevel)

        users_cache = UsersCacheService(settings.users_cache)

        app.state = HTTPServiceState(
            state={
                "auth": auth,
                "storage": storage,
                "presence": presence_srvc,
                "rabbitmq_publisher": rabbitmq_publisher,
                "sportlevel": sportlevel,
                "users_cache": users_cache,
            },
        )

        setup_dependencies(
            app,
            settings,
            deps={
                AuthServiceProto: auth,
                PresenceServiceProto: presence_srvc,
                StorageServiceProto: storage,
                SportlevelServiceProto: sportlevel,
                UsersCacheProtocol: users_cache,
                RabbitMQPublisherFactoryProto: rabbitmq_publisher,
            },
        )

        return app

    async def on_startup(self, app: HTTPServiceApp) -> None:
        await super().on_startup(app)
        await app.state.auth.start()
        await app.state.sportlevel.start()
        await app.state.storage.start()
        await app.state.users_cache.start()
        await app.state.rabbitmq_publisher.start()
        self.logger.debug("App started")

    async def on_shutdown(self, app: HTTPServiceApp) -> None:
        await super().on_shutdown(app)
        await app.state.rabbitmq_publisher.stop()
        await app.state.users_cache.stop()
        await app.state.storage.stop()
        await app.state.sportlevel.stop()
        await app.state.auth.stop()
        self.logger.debug("App stopped")


def entrypoint() -> HTTPServiceApp:
    factory = HTTPServiceFactory(get_logger())
    return factory.create_app()
