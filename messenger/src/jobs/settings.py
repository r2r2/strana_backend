from pydantic import BaseModel

from src.core.common.caching import CacheSettings
from src.jobs.autoclose_private_chats.settings import AutoclosePrivateChatsSettings
from src.jobs.match_scout_changes_listener.settings import MatchScoutChangesListenerSettings
from src.jobs.match_state_updates_listener.settings import MatchStateUpdatesListenerSettings
from src.jobs.presence_track import PresenceTrackerSettings
from src.jobs.sportlevel_users_sync import SportlevelUsersSyncSettings


class BackgroundJobsSettings(BaseModel):
    start_immediately: bool
    wait_for_finish: bool
    sportlevel_users_sync: SportlevelUsersSyncSettings
    presence_track: PresenceTrackerSettings
    autoclose_private_chats: AutoclosePrivateChatsSettings
    sl_match_state_updates_listener: MatchStateUpdatesListenerSettings
    sl_match_scout_changes_listener: MatchScoutChangesListenerSettings
    matches_cache: CacheSettings
    users_cache: CacheSettings
