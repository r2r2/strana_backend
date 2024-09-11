from starlette.datastructures import State

from src.core.common.rabbitmq import RabbitMQPublisherFactoryProto
from src.modules.auth.interface import AuthServiceProto
from src.modules.connections import ConnectionsServiceProto
from src.modules.presence import PresenceServiceProto
from src.modules.push_notifications import PushNotificationsSenderProto
from src.modules.service_updates import UpdatesListenerProto
from src.modules.sportlevel import SportlevelServiceProto
from src.modules.storage import StorageServiceProto
from src.modules.telegram import TelegramServiceProto


class WorkerState(State):
    connections: ConnectionsServiceProto
    presence: PresenceServiceProto
    updates_listener: UpdatesListenerProto
    rabbitmq_publisher: RabbitMQPublisherFactoryProto
    storage: StorageServiceProto
    sportlevel: SportlevelServiceProto
    auth: AuthServiceProto
    push_notifications: PushNotificationsSenderProto
    telegram: TelegramServiceProto
