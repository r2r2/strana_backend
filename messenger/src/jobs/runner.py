from src.core.common.periodic_tasks.runner import PeriodicTasksRunner
from src.jobs.autoclose_private_chats.job import AutoclosePrivateChatManager
from src.jobs.match_scout_changes_listener.job import MatchScoutChangesListener
from src.jobs.match_state_updates_listener.job import MatchStateUpdatesListener
from src.jobs.presence_track import PresenceTrackManager
from src.jobs.settings import BackgroundJobsSettings
from src.jobs.sportlevel_users_sync import SportlevelUsersSyncManager


class BackgroundJobsRunner:
    def __init__(
        self,
        sl_sync_manager: SportlevelUsersSyncManager,
        presence_track_manager: PresenceTrackManager,
        autoclose_private_chats_manager: AutoclosePrivateChatManager,
        sl_match_state_updates_listener: MatchStateUpdatesListener,
        sl_match_scout_changes_listener: MatchScoutChangesListener,
        settings: BackgroundJobsSettings,
    ) -> None:
        self.settings = settings
        self._runner = PeriodicTasksRunner()
        self._runner.add_task(
            task_name="sportlevel_users_sync",
            call_interval=settings.sportlevel_users_sync.check_interval,
            coro=sl_sync_manager.run_users_sync,
            settings=settings.sportlevel_users_sync,
        )
        self._runner.add_task(
            task_name="presence_track",
            call_interval=settings.presence_track.check_interval,
            coro=presence_track_manager.check_presence,
            settings=settings.presence_track,
        )
        self._runner.add_task(
            task_name="presence_track_cleanup",
            call_interval=settings.presence_track.cleanup_interval,
            coro=presence_track_manager.cleanup_presence,
            settings=settings.presence_track,
        )
        self._runner.add_task(
            task_name="autoclose_private_chats",
            call_interval=settings.autoclose_private_chats.check_interval,
            coro=autoclose_private_chats_manager.try_close_chats,
            settings=settings.autoclose_private_chats,
        )

        self._sl_match_state_updates_listener = sl_match_state_updates_listener
        self._sl_match_scout_changes_listener = sl_match_scout_changes_listener

    async def start(self) -> None:
        self._runner.start(start_immediately=self.settings.start_immediately)
        await self._sl_match_state_updates_listener.start()
        await self._sl_match_scout_changes_listener.start()

    async def stop(self) -> None:
        await self._sl_match_scout_changes_listener.stop()
        await self._sl_match_state_updates_listener.stop()
        await self._runner.stop(wait_for_completion=self.settings.wait_for_finish)
