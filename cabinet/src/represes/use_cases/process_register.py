import asyncio
from asyncio import Task
from secrets import token_urlsafe
from typing import Type, Any, Callable, Union, Optional

import structlog
from passlib.context import CryptContext
from celery.local import PromiseProxy

from common.email import EmailService
from common.files import FileProcessor
from src.users.constants import UserType
from src.agencies.constants import FileType as AgencyFileType, UploadPath as AgencyUploadPath
from src.agencies.exceptions import AgencyDataTakenError
from src.agencies.repos import Agency, AgencyRepo
from src.admins.repos import AdminRepo
from src.agents.repos import AgentRepo

from ..repos import RepresRepo, User
from ..entities import BaseRepresCase
from ..models import RequestProcessRegisterModel, RepresRegisterModel, AgencyRegisterModel
from src.users.loggers.wrappers import user_changes_logger
from src.agencies.loggers.wrappers import agency_changes_logger
from src.notifications.services import GetEmailTemplateService
from src.users.services import UserCheckUniqueService


class ProcessRegisterCase(BaseRepresCase):
    """
    Регистрация агентства вместе с руководителем
    """

    repres_mail_event_slug = "repres_confirm_email"
    admin_mail_event_slug = "admin_confirm_agency"
    link: str = "https://{}/confirm/represes/confirm_email?q={}&p={}"

    def __init__(
        self,
        site_config: dict[str, Any],
        repres_repo: Type[RepresRepo],
        email_class: Type[EmailService],
        token_creator: Callable[[int], str],
        hasher: Callable[..., CryptContext],
        agency_repo: Type[AgencyRepo],
        agent_repo: Type[AgentRepo],
        admin_repo: Type[AdminRepo],
        file_processor: Type[FileProcessor],
        create_contact_service: Union[Callable, PromiseProxy],
        create_organization_service: Union[Callable, PromiseProxy],
        bind_contact_to_company: Union[Callable, PromiseProxy],
        get_email_template_service: GetEmailTemplateService,
        check_user_unique_service: UserCheckUniqueService,
        logger: Optional[Any] = structlog.getLogger(__name__),

    ) -> None:
        self.hasher: CryptContext = hasher()
        self.repres_repo: RepresRepo = repres_repo()
        self.repres_create = user_changes_logger(
            self.repres_repo.create, self, content="Создание представителя"
        )
        self.agency_repo: AgencyRepo = agency_repo()
        self.agency_create = agency_changes_logger(
            self.agency_repo.create, self, content="Создание агентства"
        )
        self.agency_delete = agency_changes_logger(
            self.agency_repo.delete, self, content="Удаление агентства"
        )
        self.admin_repo: AdminRepo = admin_repo()
        self.agent_repo: AgentRepo = agent_repo()
        self.agent_delete = agency_changes_logger(
            self.agent_repo.delete, self, content="Удаление агента"
        )

        self.email_class: Type[EmailService] = email_class
        self.token_creator: Callable[[int], str] = token_creator

        self.file_processor: Type[FileProcessor] = file_processor

        self.site_host: str = site_config["site_host"]
        self.create_contact_service = create_contact_service
        self.create_organization_service = create_organization_service
        self.check_user_unique_service: UserCheckUniqueService = check_user_unique_service
        self.bind_contact_to_company = bind_contact_to_company
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service
        self.logger = logger

    async def __call__(
        self, payload: RequestProcessRegisterModel, **files: Any
    ) -> dict[str, Union[User, Agency]]:
        await self._check_agent_and_agency_do_not_exist(payload)

        agency = await self._create_agency(payload.agency, **files)
        repres = await self._create_repres(agency, payload.repres)
        await self.amocrm_hook(agency=agency, repres=repres)

        return dict(repres=repres, agency=agency)

    async def _create_repres(self, agency: Agency, payload: RepresRegisterModel) -> User:
        data: dict[str, Any] = payload.dict()
        data["agency_id"]: int = agency.id
        data["maintained_id"]: int = agency.id

        email: str = data["email"]
        phone: str = data["phone"]

        # Удаляем запись помеченного удалённым репреза из БД,
        # если есть такой с указанным телефоном или мылом
        filters = dict(type=UserType.REPRES, is_deleted=True)
        q_filters = [
            self.repres_repo.q_builder(or_filters=[dict(phone=phone), dict(email__iexact=email)])
        ]
        deleted_agent = await self.repres_repo.retrieve(filters=filters, q_filters=q_filters)
        if deleted_agent is not None:
            await self.agent_delete(deleted_agent)

        password: str = data.pop("password")
        extra_data: dict[str, Any] = dict(
            type=UserType.REPRES,
            email_token=token_urlsafe(32),
            password=self.hasher.hash(password),
            is_approved=True
        )
        data.update(extra_data)
        repres: User = await self.repres_create(data=data)
        token = self.token_creator(repres.id)
        await self._send_repres_confirmation_email(repres=repres, token=token)
        return repres

    async def _create_agency(self, payload: AgencyRegisterModel, **files: Any) -> Agency:
        # Стираем из БД существующее бронирование, помеченное как "удалённое"
        deleted_agency = await self.agency_repo.retrieve(
            filters=dict(is_deleted=True, inn=payload.inn)
        )
        if deleted_agency:
            await self.agency_delete(deleted_agency)

        # Создаём агентство
        data: dict[str, Any] = payload.dict()
        data.update(dict(
            files=await self.file_processor(files=files, path=AgencyUploadPath.FILES,
                                            choice_class=AgencyFileType),
            is_approved=True
        ))
        agency: Agency = await self.agency_create(data=data)
        await self._send_admins_email(agency)
        return agency

    async def _send_repres_confirmation_email(self, repres: User, token: str) -> Task:
        """
        Отправка письма представителю с просьбой подтверждения почты
        """
        confirm_link: str = self.link.format(self.site_host, token, repres.email_token)
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.repres_mail_event_slug,
            context=dict(confirm_link=confirm_link),
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=[repres.email],
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service = self.email_class(**email_options)
            return email_service.as_task()

    async def _send_admins_email(self, agency: Agency) -> Task:
        """Отправка письма админам для подтверждения агентства."""
        filters = dict(type=UserType.ADMIN, receive_admin_emails=True)
        admins = await self.admin_repo.list(filters=filters)

        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.admin_mail_event_slug,
            context=dict(agency_name=agency.name),
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=[admin.email for admin in admins],
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service = self.email_class(**email_options)
            return email_service.as_task()

    async def _check_agent_and_agency_do_not_exist(
        self, payload: RequestProcessRegisterModel
    ) -> None:
        # Проверка на то, что агентства с таким ИНН нет в БД
        agency_data: dict[str, Any] = payload.agency.dict()
        inn: str = agency_data["inn"]
        filters: dict[str, Any] = dict(inn=inn, is_deleted=False)
        agency: Agency = await self.agency_repo.retrieve(filters=filters)
        if agency:
            raise AgencyDataTakenError

        # Проверка на то, что репреза с таким email или phone нет в БД
        await self.check_user_unique_service(payload.repres)

    async def amocrm_hook(self, agency: Agency, repres: User):
        """Create amocrm company and contact webhook."""
        self.logger.warning(
            f"Amo tasks start. Agency (id, amo_id): {agency.id}, {agency.amocrm_id}; "
            f"Repres (id, amo_id): {repres.id}, {repres.amocrm_id} "
        )
        await asyncio.gather(
            self.create_contact_service(repres_id=repres.id),
            self.create_organization_service(agency_id=agency.id)
        )
        repres, agency = await asyncio.gather(
            self.repres_repo.retrieve(filters=dict(id=repres.id)),
            self.agency_repo.retrieve(filters=dict(id=agency.id))
        )
        self.logger.warning(
            f"AMO created, linking. Agency (id, amo_id): {agency.id}, {agency.amocrm_id}; "
            f"Repres (id, amo_id): {repres.id}, {repres.amocrm_id} "
        )
        self.bind_contact_to_company.delay(
            agent_amocrm_id=repres.amocrm_id,
            agency_amocrm_id=agency.amocrm_id
        )
        self.logger.warning(f"AMO link started to create with Agency ({agency.amocrm_id}) and Repres ({repres.amocrm_id})")
