from celery import Task


class BaseTaskWithRetry(Task):
    max_retries = 5
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True
