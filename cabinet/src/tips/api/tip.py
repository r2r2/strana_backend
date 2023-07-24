from typing import Any
from http import HTTPStatus
from fastapi import APIRouter

from src.tips import models, use_cases
from src.tips import repos as tips_repos


router = APIRouter(prefix="/tips", tags=["Tips"])


@router.get("", status_code=HTTPStatus.OK, response_model=models.ResponseTipListModel)
async def tip_list_view():
    """
    Список подсказок
    """
    from common import email
    from src.notifications import services as notification_services
    from src.notifications import repos as notification_repos

    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )

    email_notification_template = await get_email_template_service(
        mail_event_slug='check_dispute',
        context=dict(name="name")
    )

    if email_notification_template and email_notification_template.is_active:
        email_options: dict[str, Any] = dict(
            topic=email_notification_template.template_topic,
            content=email_notification_template.template_text,
            recipients=["sidorin@artw.ru", "myoldloverock@yandex.ru", "myoldloverock@gmail.com",
                        "maiorovpavel@gmail.com"],
            lk_type=email_notification_template.lk_type.value,
            mail_event_slug=email_notification_template.mail_event_slug,
        )
        email_service: email.EmailService = email.EmailService(**email_options)
        email_service.as_task()

    print("Тестовое письмо отправлено")

    resources: dict[str, Any] = dict(tip_repo=tips_repos.TipRepo)
    tip_list: use_cases.TipListCase = use_cases.TipListCase(**resources)
    return await tip_list()
