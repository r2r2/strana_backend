from src.core.common.rabbitmq.publisher import RabbitMQPublisherSettings
from src.core.settings import BaseServiceSettings
from src.modules.auth import AuthSettings
from src.modules.connections import ConnectionsServiceSettings
from src.modules.presence import PresenceSettings
from src.modules.service_updates import UpdatesListenerSettings
from src.modules.sportlevel import SportlevelSettings
from src.modules.storage import StorageSettings
from src.modules.telegram import TelegramServiceSettings


class WorkerSettings(BaseServiceSettings):
    storage: StorageSettings
    presence: PresenceSettings
    service_updates_publisher: RabbitMQPublisherSettings
    push_updates_publisher: RabbitMQPublisherSettings
    updates_listener: UpdatesListenerSettings
    connections: ConnectionsServiceSettings
    sportlevel: SportlevelSettings
    auth: AuthSettings
    telegram: TelegramServiceSettings
