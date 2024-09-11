from src.core.common.rabbitmq import RabbitMQPublisherSettings
from src.core.settings import BaseServiceSettings
from src.jobs.settings import BackgroundJobsSettings
from src.modules.sportlevel import SportlevelSettings
from src.modules.storage import StorageSettings


class JobsServiceSettings(BaseServiceSettings):
    storage: StorageSettings
    rabbitmq_publisher: RabbitMQPublisherSettings
    sportlevel: SportlevelSettings
    background_jobs: BackgroundJobsSettings
