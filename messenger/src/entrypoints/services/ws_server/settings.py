from src.core.common.rabbitmq import RabbitMQPublisherSettings
from src.core.settings import BaseServiceSettings
from src.modules.auth import AuthSettings
from src.modules.chat import ChatSettings
from src.modules.connections import ConnectionsServiceSettings
from src.modules.presence import PresenceSettings
from src.modules.sportlevel import SportlevelSettings
from src.modules.storage import StorageSettings


class WSServiceSettings(BaseServiceSettings):
    max_connections_per_ip: int

    storage: StorageSettings
    presence: PresenceSettings
    chat: ChatSettings
    rabbitmq_publisher: RabbitMQPublisherSettings
    connections: ConnectionsServiceSettings
    auth: AuthSettings
    sportlevel: SportlevelSettings
