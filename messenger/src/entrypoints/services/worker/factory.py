from cachetools import LFUCache

from src.core.common.memory_cache import InMemoryCacher
from src.core.common.rabbitmq.publisher import RabbitMQPublisherFactory
from src.core.factory import AppFactory, AppWithState, HealthCheckable
from src.core.logger import get_logger
from src.core.settings import load_settings
from src.entrypoints.services.worker.settings import WorkerSettings
from src.entrypoints.services.worker.state import WorkerState
from src.modules.auth.service import AuthService
from src.modules.connections.service import ConnectionsService
from src.modules.presence.service import PresenceService
from src.modules.service_updates.listener import UpdatesListenerService
from src.modules.sportlevel.service import SportlevelService
from src.modules.storage.service import StorageService
from src.modules.telegram.service import TelegramService

WorkerApp = AppWithState[WorkerState]


class WorkerFactory(AppFactory[WorkerState, WorkerSettings]):
    def create_app(self) -> WorkerApp:
        settings = load_settings(WorkerSettings)
        app = self.create_base_app(settings)

        return self._setup_state(app, settings)

    def health_check(self, app: WorkerApp) -> list[HealthCheckable]:
        context = app.state
        return [
            HealthCheckable("connections", context.connections.health_check()),
            HealthCheckable("presence", context.presence.health_check()),
            HealthCheckable("updates_listener", context.updates_listener.health_check()),
            HealthCheckable("rabbitmq_publisher", context.rabbitmq_publisher.health_check()),
            HealthCheckable("storage", context.storage.health_check()),
        ]

    def _setup_state(self, app: WorkerApp, settings: WorkerSettings) -> WorkerApp:
        auth_srvc = AuthService(settings=settings.auth)
        connections_srvc = ConnectionsService(settings=settings.connections)
        storage = StorageService(settings=settings.storage.db)
        rabbitmq_publisher = RabbitMQPublisherFactory(amqp_settings=settings.service_updates_publisher.amqp)
        presence_srvc = PresenceService(settings=settings.presence)
        cacher = InMemoryCacher(
            cache=LFUCache(maxsize=settings.updates_listener.cache.memory_cache_maxsize),
        )
        telegram_srvc = TelegramService(settings=settings.telegram)
        updates_listener = UpdatesListenerService(
            settings=settings.updates_listener,
            conn_service=connections_srvc,
            presence_service=presence_srvc,
            storage_service=storage,
            rabbitmq_publisher=rabbitmq_publisher,
            auth_service=auth_srvc,
            telegram_service=telegram_srvc,
            cacher=cacher,
        )
        sportlevel = SportlevelService(settings=settings.sportlevel)

        app.state = WorkerState(
            state={
                "auth": auth_srvc,
                "storage": storage,
                "connections": connections_srvc,
                "presence": presence_srvc,
                "rabbitmq_publisher": rabbitmq_publisher,
                "updates_listener": updates_listener,
                "sportlevel": sportlevel,
                "telegram": telegram_srvc,
            },
        )

        return app

    async def on_startup(self, app: WorkerApp) -> None:
        await super().on_startup(app)
        await app.state.telegram.start()
        await app.state.auth.start()
        await app.state.storage.start()
        await app.state.updates_listener.start()
        await app.state.rabbitmq_publisher.start()
        await app.state.sportlevel.start()
        self.logger.debug("App started")

    async def on_shutdown(self, app: WorkerApp) -> None:
        await super().on_shutdown(app)
        await app.state.sportlevel.stop()
        await app.state.rabbitmq_publisher.stop()
        await app.state.updates_listener.stop()
        await app.state.storage.stop()
        await app.state.auth.stop()
        await app.state.telegram.stop()
        self.logger.debug("App stopped")


def entrypoint() -> WorkerApp:
    factory = WorkerFactory(get_logger())
    return factory.create_app()
