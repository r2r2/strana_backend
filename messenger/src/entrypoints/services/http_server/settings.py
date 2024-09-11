from src.core.common.rabbitmq import RabbitMQPublisherSettings
from src.core.settings import BaseServiceSettings
from src.modules.auth import AuthSettings
from src.modules.file_uploads import FileUploadsSettings
from src.modules.presence import PresenceSettings
from src.modules.push_notifications import PushNotificationsVapidSettings
from src.modules.sportlevel import SportlevelSettings
from src.modules.storage import StorageSettings
from src.modules.unread_counters import UnreadCountersSettings
from src.modules.users_cache import UsersCacheSettings


class HTTPServiceSettings(BaseServiceSettings):
    storage: StorageSettings
    presence: PresenceSettings
    rabbitmq_publisher: RabbitMQPublisherSettings
    auth: AuthSettings
    sportlevel: SportlevelSettings
    users_cache: UsersCacheSettings
    file_uploads: FileUploadsSettings
    unread_counters: UnreadCountersSettings
    vapid: PushNotificationsVapidSettings
