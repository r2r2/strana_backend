from typing import Any, Type, Callable

from src.users.constants import UserType
from src.users.loggers.wrappers import user_changes_logger
from src.notifications.services import GetSmsTemplateService
from ..constants import UploadPath, FileType
from ..entities import BaseAgencyCase
from ..exceptions import AgencyDataTakenError
from ..models import RequestAdminsAgenciesRegisterModel
from ..repos import Agency, AgencyRepo
from ..services import CreateOrganizationService
from ..loggers.wrappers import agency_changes_logger
from ..types import (
    AgencyRepresRepo,
    AgencyUser,
    AgencySms,
    AgencyHasher,
    AgencyCreateContactService,
    AgencyFileProcessor,
)


class AdminsAgenciesRegisterCase(BaseAgencyCase):
    """
    Регистрация агентства администратором
    """

    sms_event_slug = "register_agency"

    def __init__(
        self,
        user_types: Any,
        sms_class: Type[AgencySms],
        agency_repo: Type[AgencyRepo],
        hasher: Callable[..., AgencyHasher],
        repres_repo: Type[AgencyRepresRepo],
        password_generator: Callable[..., str],
        file_processor: Type[AgencyFileProcessor],
        create_contact_service: AgencyCreateContactService,
        create_organization_service: CreateOrganizationService,
        get_sms_template_service: GetSmsTemplateService,
    ) -> None:
        self.agency_repo: AgencyRepo = agency_repo()
        self.agency_create = agency_changes_logger(
            self.agency_repo.create, self, content="Создание агентства"
        )
        self.agency_delete = agency_changes_logger(
            self.agency_repo.delete, self, content="Удаление агентства"
        )
        self.repres_repo: AgencyRepresRepo = repres_repo()
        self.repres_create = user_changes_logger(
            self.repres_repo.create, self, content="Создание представителя"
        )
        self.repres_delete = user_changes_logger(
            self.repres_repo.delete, self, content="Удаление представителя"
        )

        self.user_types: Any = user_types
        self.hasher: AgencyHasher = hasher()
        self.sms_class: Type[AgencySms] = sms_class
        self.password_generator: Callable[..., str] = password_generator

        self.file_processor: Type[AgencyFileProcessor] = file_processor

        self.create_contact_service: AgencyCreateContactService = create_contact_service
        self.create_organization_service: CreateOrganizationService = create_organization_service
        self.get_sms_template_service: GetSmsTemplateService = get_sms_template_service

    async def __call__(self, payload: RequestAdminsAgenciesRegisterModel, **files: Any) -> Agency:
        data: dict[str, Any] = payload.dict()
        repres_data: dict[str, Any] = dict(
            name=data.pop("naming", None),
            email=data.pop("email", None),
            phone=data.pop("phone", None),
            surname=data.pop("surname", None),
            duty_type=data.pop("duty_type", None),
            patronymic=data.pop("patronymic", None),
        )
        inn: str = data["inn"]
        phone: str = repres_data["phone"]
        email: str = repres_data["email"]

        # Проверка на существование агентства или агента
        filters = dict(type=UserType.REPRES, is_deleted=False)
        q_filters = [
            self.repres_repo.q_builder(or_filters=[dict(phone=phone), dict(email__iexact=email)])
        ]
        repres: AgencyUser = await self.repres_repo.retrieve(filters=filters, q_filters=q_filters)

        filters = dict(inn=inn, is_deleted=False)
        agency: Agency = await self.agency_repo.retrieve(filters=filters)
        if repres or agency:
            raise AgencyDataTakenError

        # Удаление помеченных удалёнными агентства и репреза, если такие есть
        filters = dict(type=UserType.REPRES, is_deleted=True)
        q_filters = [
            self.repres_repo.q_builder(or_filters=[dict(phone=phone), dict(email__iexact=email)])
        ]
        repres: AgencyUser = await self.repres_repo.retrieve(filters=filters, q_filters=q_filters)
        if repres:
            await self.repres_delete(repres)

        filters = dict(inn=inn, is_deleted=True)
        agency: Agency = await self.agency_repo.retrieve(filters=filters)
        if agency:
            await self.agency_delete(agency)

        # Создание агентства и репреза
        data["is_approved"]: bool = True
        data["files"]: Any = await self.file_processor(
            files=files,
            path=UploadPath.FILES,
            choice_class=FileType,
            container=getattr(agency, "files", None),
        )
        agency: Agency = await self.agency_create(data=data)

        repres_data["agency_id"]: int = agency.id
        repres_data["maintained_id"]: int = agency.id
        one_time_password: str = self.password_generator()
        extra_data: dict[str, Any] = dict(
            is_approved=True,
            type=self.user_types.REPRES,
            one_time_password=self.hasher.hash(one_time_password),
        )
        repres_data.update(extra_data)
        repres: AgencyUser = await self.repres_create(data=repres_data)

        sms_notification_template = await self.get_sms_template_service(
            sms_event_slug=self.sms_event_slug,
        )
        if sms_notification_template and sms_notification_template.is_active:
            sms_options: dict[str, Any] = dict(
                phone=phone,
                message=sms_notification_template.template_text.format(email=email, password=one_time_password),
                lk_type=sms_notification_template.lk_type.value,
                sms_event_slug=sms_notification_template.sms_event_slug,
            )
            self.sms_class(**sms_options).as_task()

        await self.create_organization_service(inn=inn, agency=agency)
        await self.create_contact_service(phone=repres.phone, repres=repres)
        return agency
