import celery


@celery.task
def send_amocrm_lead(
    name,
    phone,
    description,
    pipeline_status_id,
    pipeline_id,
    text=None,
    resp_user_id=None,
    name_lead=None,
    custom_fields=None,
) -> None:
    from amocrm.services import AmoCRM

    AmoCRM().create_contact_and_lead(
        name,
        phone,
        description,
        pipeline_status_id,
        pipeline_id,
        resp_user_id=resp_user_id,
        name_lead=name_lead,
        text=text,
        custom_fields=custom_fields,
    )


@celery.task
def update_lead_user(lead_id, resp_user_id) -> None:
    from amocrm.services import AmoCRM

    AmoCRM().update_lead_resp_user(lead_id, resp_user_id)


@celery.task
def create_task(lead_id, resp_user_id) -> None:
    from amocrm.services import AmoCRM

    AmoCRM().create_task(lead_id, resp_user_id)


@celery.task
def create_note(lead_id, text, resp_user_id) -> None:
    from amocrm.services import AmoCRM

    AmoCRM().create_note(lead_id, text, resp_user_id)


@celery.task
def update_credentials() -> None:
    from amocrm.services import AmoCRM

    AmoCRM().refresh_auth()


@celery.task
def update_lead(lead_id, description, custom_fields) -> None:
    from amocrm.services import AmoCRM

    AmoCRM().update_lead(lead_id, description, custom_fields)