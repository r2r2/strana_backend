from celery import shared_task
from .services import deactivate_main_page_slides


@shared_task
def deactivate_main_page_slides_task() -> None:
    deactivate_main_page_slides()
