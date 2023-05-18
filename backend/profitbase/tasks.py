import celery
from celery import shared_task
from profitbase.services import (ProfitBaseService,
                                 notify_realty_update_managers)
from properties.services import (update_layouts,
                                 update_price_with_special_offers,
                                 update_properties_min_mortgage)

from . import logger


@shared_task
def update_projects_task():
    ProfitBaseService().update_projects()


@shared_task
def update_buildings_task():
    """Задача по обновлению данных о домах."""
    ProfitBaseService().update_buildings()


@shared_task
def update_offers_task():
    """Обновление данных об акциях."""
    try:
        ProfitBaseService().update_offers()
    except Exception as e:
        logger.exception("Ошибка обновления данных об акциях")


@shared_task
def notify_realty_update_managers_task() -> None:
    """
    Уведомление менеджеров по обновлению недвижимости
    """
    notify_realty_update_managers()


@celery.task(autoretry_for=(Exception,), retry_kwargs={"max_retries": 5, "default_retry_delay": 60})
def update_realty_for_project(project_id: str, access_token: str) -> None:
    """Обновление помещений проекта."""
    from properties.models import Layout
    try:
        ProfitBaseService().update_property_for_project(project_id, access_token)
    except Exception as e:
        logger.exception(f"Ошибка обновления данных об объектах недвижимости. project_id: {project_id}")
    update_price_with_special_offers(project_id)
    update_properties_min_mortgage(project_id)
    update_layouts(Layout.objects.filter(flat_count__isnull=True).values_list("id", flat=True))
