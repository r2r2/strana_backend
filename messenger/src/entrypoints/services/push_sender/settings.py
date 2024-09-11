from src.core.settings import BaseServiceSettings
from src.modules.push_notifications import PushNotificationsListenerSettings, PushNotificationsSenderSettings
from src.modules.storage import StorageSettings


class PushSenderServiceSettings(BaseServiceSettings):
    storage: StorageSettings
    push_listener: PushNotificationsListenerSettings
    push_sender: PushNotificationsSenderSettings
