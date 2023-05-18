from celery import shared_task
from .services import (
    calculate_building_min_flat_prices,
    calculate_section_min_flat_prices,
    calculate_floor_min_flat_prices,
    calculate_building_finish_dates,
    calculate_current_level, building_archive_handler
)


@shared_task
def calculate_building_fields_task() -> None:
    calculate_building_finish_dates()
    calculate_building_min_flat_prices()


@shared_task
def calculate_section_fields_task() -> None:
    calculate_section_min_flat_prices()


@shared_task
def calculate_floor_fields_task() -> None:
    calculate_floor_min_flat_prices()


@shared_task
def calculate_current_level_task() -> None:
    calculate_current_level()


@shared_task
def building_archive_handler_task(building_id: int) -> None:
    building_archive_handler(building_id)
