from src.core.factory import AppFactory, AppWithState, HealthCheckable
from src.core.logger import get_logger
from src.core.settings import load_settings
from src.entrypoints.services.push_sender.settings import PushSenderServiceSettings
from src.entrypoints.services.push_sender.state import PushSenderServiceState
from src.modules.push_notifications.listener import PushNotificationsListener
from src.modules.push_notifications.sender import PushNotificationsSender
from src.modules.storage.service import StorageService

JobsServiceApp = AppWithState[PushSenderServiceState]


class PushSenderServiceFactory(AppFactory[PushSenderServiceState, PushSenderServiceSettings]):
    def create_app(self) -> JobsServiceApp:
        settings = load_settings(PushSenderServiceSettings)
        app = self.create_base_app(settings)
        return self._setup_state(app, settings)

    def health_check(self, app: JobsServiceApp) -> list[HealthCheckable]:
        context = app.state
        return [
            HealthCheckable("storage", context.storage.health_check()),
            HealthCheckable("push_listener", context.push_listener.health_check()),
        ]

    def _setup_state(self, app: JobsServiceApp, settings: PushSenderServiceSettings) -> JobsServiceApp:
        storage = StorageService(settings=settings.storage.db)

        push_sender = PushNotificationsSender(settings=settings.push_sender)
        push_listener = PushNotificationsListener(
            sender=push_sender,
            settings=settings.push_listener,
            storage=storage,
        )

        app.state = PushSenderServiceState(
            state={
                "storage": storage,
                "push_listener": push_listener,
            },
        )

        return app

    async def on_startup(self, app: JobsServiceApp) -> None:
        await super().on_startup(app)
        await app.state.storage.start()
        await app.state.push_listener.start()
        self.logger.debug("App started")

    async def on_shutdown(self, app: JobsServiceApp) -> None:
        await super().on_shutdown(app)
        await app.state.push_listener.stop()
        await app.state.storage.stop()
        self.logger.debug("App stopped")


def entrypoint() -> JobsServiceApp:
    factory = PushSenderServiceFactory(get_logger())
    return factory.create_app()
