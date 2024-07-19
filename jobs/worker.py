from jobs.settings import get_config
from jobs.tasks import celery_app
from jobs.utils import setup_jobs, setup_logger

settings = get_config()
setup_logger()
setup_jobs(celery_app, settings)
