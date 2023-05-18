import os

from django.conf import settings
from kombu import Queue

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.base")


app = Celery(broker=settings.CELERY_BROKER_URL)
app.config_from_object("django.conf:settings")
app.autodiscover_tasks()
app.conf.task_queues = (
    Queue("beat", exclusive=True),
    Queue("realty", exclusive=True),
    Queue("amo", exclusive=True),
    Queue("celery"),
)
app.control.add_consumer("beat", reply=True, destination=["beat1@strana.com"])
app.control.add_consumer("realty", reply=True, destination=["realty1@strana.com"])
app.control.add_consumer("amo", reply=True, destination=["amo_tasks1@strana.com"])
app.conf.task_routes = {
    "amocrm.tasks.update_credentials": {"queue": "beat"},
    "auction.tasks.notify_start_auction_task": {"queue": "beat"},
    "buildings.tasks.calculate_building_fields_task": {"queue": "beat"},
    "buildings.tasks.calculate_current_level_task": {"queue": "beat"},
    "buildings.tasks.calculate_floor_fields_task": {"queue": "beat"},
    "buildings.tasks.calculate_section_fields_task": {"queue": "beat"},
    "buildings.tasks.building_archive_handler_task": {"queue": "celery"},
    "cities.tasks.calculate_city_fields_task": {"queue": "beat"},
    "dvizh_api.tasks.update_offers_data_task": {"queue": "beat"},
    "main_page.tasks.deactivate_main_page_slides_task": {"queue": "beat"},
    "mortgage.tasks.calculate_mortgage_page_fields_task": {"queue": "beat"},
    "news.tasks.deactivate_old_actions_task": {"queue": "beat"},
    "panel_manager.tasks.process_meeting": {"queue": "amo"},
    "panel_manager.tasks.process_webhook": {"queue": "amo"},
    "profitbase.tasks.notify_realty_update_managers_task": {"queue": "beat"},
    "profitbase.tasks.update_buildings_task": {"queue": "realty"},
    "profitbase.tasks.update_offers_task": {"queue": "realty"},
    "profitbase.tasks.update_projects_task": {"queue": "realty"},
    "profitbase.tasks.update_realty_for_project": {"queue": "realty"},
    "projects.tasks.calculate_project_fields_task": {"queue": "beat"},
    "properties.tasks.update_layout_min_mortgage_tasks": {"queue": "beat"},
    "properties.tasks.update_layouts_task": {"queue": "beat"},
    "properties.tasks.update_price_with_special_offers_task": {"queue": "realty"},
    "properties.tasks.update_properties_min_mortgage_tasks": {"queue": "realty"},
    "properties.tasks.update_special_offers_activity_task": {"queue": "beat"},
    "vk.tasks.scraping_posts_vk": {"queue": "beat"},
}

if __name__ == "__main__":
    app.start()
