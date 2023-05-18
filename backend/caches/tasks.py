from app.celery import app
from caches.classes import CrontabCache


@app.task
def update_chunk_task(chunk) -> None:
    """
    Обновление части кэшей в таске
    """
    CrontabCache.update_chunk(chunk)


@app.task
def update_caches_task() -> None:
    """
    Обновление кэшей в таске
    """
    CrontabCache.refresh()
    for chunk in CrontabCache.chunks:
        update_chunk_task.delay(chunk)
