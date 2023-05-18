from celery import shared_task
from .services import calculate_mortgage_page_min_value

@shared_task
def calculate_mortgage_page_fields_task() -> None:
    calculate_mortgage_page_min_value()