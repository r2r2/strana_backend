from celery import shared_task
from .services import (
    calculate_city_min_mortgages,
    calculate_city_min_flat_prices,
    calculate_city_min_commercial_price,
    calculate_city_commercial_area_ranges
)


@shared_task
def calculate_city_fields_task() -> None:
    calculate_city_min_mortgages()
    calculate_city_min_flat_prices()
    calculate_city_min_commercial_price()
    calculate_city_commercial_area_ranges()
