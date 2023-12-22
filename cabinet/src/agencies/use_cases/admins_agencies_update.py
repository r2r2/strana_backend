from asyncio import Task
from typing import Any, Callable, Type

from ..entities import BaseAgencyCase
from ..exceptions import AgencyNotFoundError
from ..models import RequestAdminsAgenciesUpdateModel
from ..repos import Agency, AgencyRepo
from ..types import (AgencyEmail, AgencyFileDestroyer, AgencyFileProcessor,
                     AgencyRepresRepo, AgencySms, AgencyUser)
from ..loggers.wrappers import agency_changes_logger
from src.notifications.services import GetEmailTemplateService, GetSmsTemplateService
from common.schemas import UrlEncodeDTO
from common.utils import generate_notify_url


class AdminsAgenciesUpdateCase(BaseAgencyCase):
    """
    Обновление агентства администратором
    """

    mail_event_slug = "agency_update"
    sms_event_slug = "agency_update"
    email_link_route_template: str = "/change/represes/change_email"
    phone_link: str = "https://{}/change/represes/change_phone?q={}&p={}"
    phone_link_route_template: str = "/change/represes/change_phone"
    def __init__(
        self,
        sms_class: Type[AgencySms],
        site_config: dict[str, Any],
        agency_repo: Type[AgencyRepo],
        email_class: Type[AgencyEmail],
        repres_repo: Type[AgencyRepresRepo],
        token_creator: Callable[[int], str],
        file_processor: Type[AgencyFileProcessor],
        file_destroyer: Type[AgencyFileDestroyer],
        get_email_template_service: GetEmailTemplateService,
        get_sms_template_service: GetSmsTemplateService,
    ) -> None:
        self.agency_repo: AgencyRepo = agency_repo()
        self.agency_update = agency_changes_logger(
            self.agency_repo.update, self, content="Обновление данных агентства администратором"
        )
        self.repres_repo: AgencyRepresRepo = repres_repo()

        self.sms_class: AgencySms = sms_class
        self.email_class: AgencyEmail = email_class
        self.token_creator: Callable[[int], str] = token_creator
        self.file_processor: AgencyFileProcessor = file_processor
        self.file_destroyer: AgencyFileDestroyer = file_destroyer
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service
        self.get_sms_template_service: GetSmsTemplateService = get_sms_template_service

        self.site_host: str = site_config["site_host"]

    async def __call__(
        self, agency_id: int, payload: RequestAdminsAgenciesUpdateModel
    ) -> Agency:
        data: dict[str, Any] = payload.dict(exclude_unset=True, exclude_none=True)
        filters: dict[str, Any] = dict(id=agency_id, is_deleted=False)
        agency: Agency = await self.agency_repo.retrieve(
            filters=filters, prefetch_fields=["maintainer"]
        )
        if not agency:
            raise AgencyNotFoundError
        agency: Agency = await self.agency_update(agency=agency, data=data)
        return agency

    async def _send_sms(self, maintainer: AgencyUser, token: str) -> Task:
        """
        Отправка смс
        """
        sms_notification_template = await self.get_sms_template_service(
            sms_event_slug=self.sms_event_slug,
        )

        if sms_notification_template and sms_notification_template.is_active:
            url_data: dict[str, Any] = dict(
                host=self.site_host,
                route_template=self.email_link_route_template,
                query_params=dict(
                    q=token,
                    p=maintainer.change_phone_token,
                ),
                use_ampersand_ascii=True,
            )
            url_dto: UrlEncodeDTO = UrlEncodeDTO(**url_data)
            update_link: str = generate_notify_url(url_dto=url_dto)
            message: str = sms_notification_template.template_text.format(
                new_phone=maintainer.change_phone, old_phone=maintainer.phone, update_link=update_link
            )
            sms_options: dict[str, Any] = dict(
                phone=maintainer.phone,
                message=message,
                lk_type=sms_notification_template.lk_type.value,
                sms_event_slug=sms_notification_template.sms_event_slug,
            )
            sms_service: AgencySms = self.sms_class(**sms_options)
            return sms_service.as_task()

    async def _send_email(self, maintainer: AgencyUser, token: str) -> Task:
        """
        Отправка почты
        """

        url_data: dict[str, Any] = dict(
            host=self.site_host,
            route_template=self.email_link_route_template,
            query_params=dict(
                q=token,
                p=maintainer.change_phone_token,
            )
        )
        url_dto: UrlEncodeDTO = UrlEncodeDTO(**url_data)
        update_link: str = generate_notify_url(url_dto=url_dto)
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.mail_event_slug,
            context=dict(
                update_link=update_link,
                old_email=maintainer.email,
                new_email=maintainer.change_email,
            ),
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=[maintainer.email],
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: AgencyEmail = self.email_class(**email_options)
            return email_service.as_task()
