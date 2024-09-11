from src.core.common.rabbitmq import RabbitMQPublisherFactory
from src.core.factory import AppFactory, AppWithState, HealthCheckable
from src.core.logger import get_logger
from src.core.settings import load_settings
from src.entrypoints.services.jobs.settings import JobsServiceSettings
from src.entrypoints.services.jobs.state import JobsServiceState
from src.jobs.autoclose_private_chats.job import AutoclosePrivateChatManager
from src.jobs.cache import SLSyncInMemoryCache
from src.jobs.match_scout_changes_listener.job import MatchScoutChangesListener
from src.jobs.match_state_updates_listener.job import MatchStateUpdatesListener
from src.jobs.presence_track.job import PresenceTrackManager
from src.jobs.runner import BackgroundJobsRunner
from src.jobs.sportlevel_users_sync.job import SportlevelUsersSyncManager
from src.modules.sportlevel.service import SportlevelService
from src.modules.storage.service import StorageService

JobsServiceApp = AppWithState[JobsServiceState]


class JobsServiceFactory(AppFactory[JobsServiceState, JobsServiceSettings]):
    def create_app(self) -> JobsServiceApp:
        settings = load_settings(JobsServiceSettings)
        app = self.create_base_app(settings)
        return self._setup_state(app, settings)

    def health_check(self, app: JobsServiceApp) -> list[HealthCheckable]:
        context = app.state
        return [
            HealthCheckable("rabbitmq_publisher", context.rabbitmq_publisher.health_check()),
            HealthCheckable("storage", context.storage.health_check()),
        ]

    def _setup_state(self, app: JobsServiceApp, settings: JobsServiceSettings) -> JobsServiceApp:
        storage = StorageService(settings=settings.storage.db)

        rabbitmq_publisher = RabbitMQPublisherFactory(amqp_settings=settings.rabbitmq_publisher.amqp)

        sportlevel = SportlevelService(settings=settings.sportlevel)

        users_cache = SLSyncInMemoryCache(cfg=settings.background_jobs.users_cache)
        matches_cache = SLSyncInMemoryCache(cfg=settings.background_jobs.matches_cache)

        sl_users_sync_manager = SportlevelUsersSyncManager(
            users_cache=users_cache,
            storage=storage,
            sl_client=sportlevel,
            rabbitmq_publisher=rabbitmq_publisher,
        )

        sl_updates_listener = MatchStateUpdatesListener(
            rabbitmq_publisher=rabbitmq_publisher,
            storage=storage,
            sl_client=sportlevel,
            users_cache=users_cache,
            matches_cache=matches_cache,
            users_sync_manager=sl_users_sync_manager,
            settings=settings.background_jobs.sl_match_state_updates_listener,
        )

        sl_scout_changes_listener = MatchScoutChangesListener(
            rabbitmq_publisher=rabbitmq_publisher,
            storage=storage,
            sl_client=sportlevel,
            matches_cache=matches_cache,
            users_sync_manager=sl_users_sync_manager,
            settings=settings.background_jobs.sl_match_scout_changes_listener,
        )

        background_jobs = BackgroundJobsRunner(
            sl_sync_manager=sl_users_sync_manager,
            presence_track_manager=PresenceTrackManager(
                rabbitmq_publisher=rabbitmq_publisher,
                settings=settings.background_jobs.presence_track,
            ),
            autoclose_private_chats_manager=AutoclosePrivateChatManager(
                rabbitmq_publisher=rabbitmq_publisher,
                storage=storage,
                settings=settings.background_jobs.autoclose_private_chats,
            ),
            sl_match_state_updates_listener=sl_updates_listener,
            sl_match_scout_changes_listener=sl_scout_changes_listener,
            settings=settings.background_jobs,
        )

        app.state = JobsServiceState(
            state={
                "storage": storage,
                "rabbitmq_publisher": rabbitmq_publisher,
                "sportlevel": sportlevel,
                "background_jobs": background_jobs,
            },
        )

        return app

    async def on_startup(self, app: JobsServiceApp) -> None:
        await super().on_startup(app)
        await app.state.storage.start()
        await app.state.rabbitmq_publisher.start()
        await app.state.sportlevel.start()
        await app.state.background_jobs.start()
        self.logger.debug("App started")

    async def on_shutdown(self, app: JobsServiceApp) -> None:
        await super().on_shutdown(app)
        await app.state.background_jobs.stop()
        await app.state.sportlevel.stop()
        await app.state.rabbitmq_publisher.stop()
        await app.state.storage.stop()
        self.logger.debug("App stopped")


def entrypoint() -> JobsServiceApp:
    factory = JobsServiceFactory(get_logger())
    return factory.create_app()
