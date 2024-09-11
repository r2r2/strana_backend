from starlette.datastructures import State

from src.core.common.rabbitmq import RabbitMQPublisherFactoryProto
from src.modules.auth import AuthServiceProto
from src.modules.presence import PresenceServiceProto
from src.modules.sportlevel import SportlevelServiceProto
from src.modules.storage import StorageServiceProto
from src.modules.users_cache import UsersCacheProtocol


class HTTPServiceState(State):
    auth: AuthServiceProto
    presence: PresenceServiceProto
    rabbitmq_publisher: RabbitMQPublisherFactoryProto
    storage: StorageServiceProto
    sportlevel: SportlevelServiceProto
    users_cache: UsersCacheProtocol
