from src.api.ws.chat_websocket import chat_ws_api_router
from src.core.common.rabbitmq import RabbitMQPublisherFactory, RabbitMQPublisherFactoryProto
from src.core.di import setup_dependencies
from src.core.factory import AppFactory, AppWithState, HealthCheckable
from src.core.logger import get_logger
from src.core.settings import load_settings
from src.entrypoints.services.ws_server.middleware import WSConnectionsLimitMiddleware
from src.entrypoints.services.ws_server.settings import WSServiceSettings
from src.entrypoints.services.ws_server.state import WSServiceState
from src.modules.auth import AuthServiceProto
from src.modules.auth.service import AuthService
from src.modules.connections import ConnectionsServiceProto
from src.modules.connections.service import ConnectionsService
from src.modules.presence import PresenceServiceProto
from src.modules.presence.service import PresenceService
from src.modules.sportlevel import SportlevelServiceProto
from src.modules.sportlevel.service import SportlevelService
from src.modules.storage import StorageServiceProto
from src.modules.storage.service import StorageService

WSServiceApp = AppWithState[WSServiceState]


class WSServiceFactory(AppFactory[WSServiceState, WSServiceSettings]):
    def create_app(self) -> WSServiceApp:
        settings = load_settings(WSServiceSettings)
        app = self.create_base_app(settings)
        app.include_router(chat_ws_api_router)
        app.add_middleware(WSConnectionsLimitMiddleware)
        return self._setup_state(app, settings)

    def health_check(self, app: WSServiceApp) -> list[HealthCheckable]:
        context = app.state
        return [
            HealthCheckable("auth", context.auth.health_check()),
            HealthCheckable("connections", context.connections.health_check()),
            HealthCheckable("presence", context.presence.health_check()),
            HealthCheckable("rabbitmq_publisher", context.rabbitmq_publisher.health_check()),
            HealthCheckable("storage", context.storage.health_check()),
        ]

    def _setup_state(self, app: WSServiceApp, settings: WSServiceSettings) -> WSServiceApp:
        connections_srvc = ConnectionsService(settings=settings.connections)
        storage = StorageService(settings=settings.storage.db)
        rabbitmq_publisher = RabbitMQPublisherFactory(amqp_settings=settings.rabbitmq_publisher.amqp)
        presence_srvc = PresenceService(settings=settings.presence)
        auth = AuthService(settings=settings.auth)
        sportlevel = SportlevelService(settings=settings.sportlevel)

        app.state = WSServiceState(
            state={
                "auth": auth,
                "storage": storage,
                "connections": connections_srvc,
                "presence": presence_srvc,
                "rabbitmq_publisher": rabbitmq_publisher,
                "sportlevel": sportlevel,
                "settings": settings,
            },
        )

        setup_dependencies(
            app,
            settings,
            deps={
                AuthServiceProto: auth,
                ConnectionsServiceProto: connections_srvc,
                PresenceServiceProto: presence_srvc,
                RabbitMQPublisherFactoryProto: rabbitmq_publisher,
                StorageServiceProto: storage,
                SportlevelServiceProto: sportlevel,
            },
        )

        return app

    async def on_startup(self, app: WSServiceApp) -> None:
        await super().on_startup(app)
        await app.state.auth.start()
        await app.state.storage.start()
        await app.state.rabbitmq_publisher.start()
        await app.state.sportlevel.start()
        self.logger.debug("App started")

    async def on_shutdown(self, app: WSServiceApp) -> None:
        await super().on_shutdown(app)
        await app.state.sportlevel.stop()
        await app.state.rabbitmq_publisher.stop()
        await app.state.storage.stop()
        await app.state.auth.stop()
        self.logger.debug("App stopped")


def entrypoint() -> WSServiceApp:
    factory = WSServiceFactory(get_logger())
    return factory.create_app()
