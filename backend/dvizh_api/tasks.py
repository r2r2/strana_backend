import celery


@celery.shared_task
def update_offers_data_task() -> None:
    from .services import update_dvizh_data

    update_dvizh_data()
