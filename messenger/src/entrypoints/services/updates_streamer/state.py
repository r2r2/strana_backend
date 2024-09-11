from starlette.datastructures import State

from src.modules.auth import AuthServiceProto
from src.modules.storage import StorageServiceProto
from src.modules.updates_streamer.interface import StreamerConnServiceProto


class UpdatesStreamerState(State):
    auth: AuthServiceProto
    storage: StorageServiceProto
    connections: StreamerConnServiceProto
