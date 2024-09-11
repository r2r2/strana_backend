from starlette.datastructures import State

from src.core.common.rabbitmq import RabbitMQPublisherFactoryProto
from src.entrypoints.services.ws_server.settings import WSServiceSettings
from src.modules.auth import AuthServiceProto
from src.modules.connections import ConnectionsServiceProto
from src.modules.presence import PresenceServiceProto
from src.modules.sportlevel import SportlevelServiceProto
from src.modules.storage import StorageServiceProto


class WSServiceState(State):
    auth: AuthServiceProto
    connections: ConnectionsServiceProto
    presence: PresenceServiceProto
    rabbitmq_publisher: RabbitMQPublisherFactoryProto
    storage: StorageServiceProto
    sportlevel: SportlevelServiceProto
    settings: WSServiceSettings
