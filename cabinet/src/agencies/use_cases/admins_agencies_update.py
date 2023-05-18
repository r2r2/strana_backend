from asyncio import Task
from typing import Any, Callable, Type

from ..entities import BaseAgencyCase
from ..exceptions import AgencyNotFoundError
from ..models import RequestAdminsAgenciesUpdateModel
from ..repos import Agency, AgencyRepo
from ..types import (AgencyEmail, AgencyFileDestroyer, AgencyFileProcessor,
                     AgencyRepresRepo, AgencySms, AgencyUser)
from ..loggers.wrappers import agency_changes_logger


class AdminsAgenciesUpdateCase(BaseAgencyCase):
    """
    Обновление агентства администратором
    """

    email_template: str = "src/agencies/templates/change_email.html"
    message_template: str = (
        "Для подтверждения смены номера телефона {old_phone} на {new_phone} перейдите по ссылке {update_link} . "
        "После перехода по ссылке Ваш аккаунт будет неактивен до подтверждения номера телефона {new_phone} ."
    )
    email_link: str = "https://{}/change/represes/change_email?q={}&p={}"
    phone_link: str = "https://{}/change/represes/change_phone?q={}&p={}"

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
        update_link: str = self.email_link.format(
            self.site_host, token, maintainer.change_phone_token
        )
        message: str = self.message_template.format(
            new_phone=maintainer.change_phone, old_phone=maintainer.phone, update_link=update_link
        )
        sms_options: dict[str, Any] = dict(phone=maintainer.phone, message=message)
        sms_service: AgencySms = self.sms_class(**sms_options)
        return sms_service.as_task()

    async def _send_email(self, maintainer: AgencyUser, token: str) -> Task:
        """
        Отправка почты
        """
        update_link: str = self.email_link.format(
            self.site_host, token, maintainer.change_email_token
        )
        email_options: dict[str, Any] = dict(
            topic="Смена почты",
            recipients=[maintainer.email],
            template=self.email_template,
            context=dict(
                update_link=update_link,
                old_email=maintainer.email,
                new_email=maintainer.change_email,
            ),
        )
        email_service: AgencyEmail = self.email_class(**email_options)
        return email_service.as_task()
