from starlette.datastructures import State

from src.core.common.rabbitmq import RabbitMQPublisherFactoryProto
from src.jobs.runner import BackgroundJobsRunner
from src.modules.sportlevel import SportlevelServiceProto
from src.modules.storage import StorageServiceProto


class JobsServiceState(State):
    rabbitmq_publisher: RabbitMQPublisherFactoryProto
    storage: StorageServiceProto
    sportlevel: SportlevelServiceProto
    background_jobs: BackgroundJobsRunner
