from src.core.settings import BaseServiceSettings
from src.modules.auth import AuthSettings
from src.modules.storage import StorageSettings
from src.modules.updates_streamer.settings import UpdatesStreamerSettings


class UpdatesStreamerServiceSettings(BaseServiceSettings):
    auth: AuthSettings
    storage: StorageSettings
    streamer: UpdatesStreamerSettings
