from starlette.datastructures import State

from src.modules.push_notifications import PushNotificationsListenerProto
from src.modules.storage import StorageServiceProto


class PushSenderServiceState(State):
    storage: StorageServiceProto
    push_listener: PushNotificationsListenerProto
