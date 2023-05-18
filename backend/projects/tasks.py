from celery import shared_task
from .services import (
    calculate_project_min_prop_price,
    calculate_project_prop_area_range,
    calculate_project_min_rooms_prices,
    calculate_project_min_rate_offers,
    calculate_project_min_mortgage,
    update_count_pantry_parking,
    calculate_project_label_with_completion,
)


@shared_task
def calculate_project_fields_task() -> None:
    calculate_project_min_prop_price()
    calculate_project_prop_area_range()
    calculate_project_min_rooms_prices()
    calculate_project_min_rate_offers()
    calculate_project_min_mortgage()
    calculate_project_label_with_completion()
    update_count_pantry_parking()
