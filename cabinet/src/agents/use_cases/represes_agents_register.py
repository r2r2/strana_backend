from typing import Type, Any, Callable

from src.users.constants import UserType
from src.notifications.services import GetSmsTemplateService

from ..services import CreateContactService, EnsureBrokerTagService
from ..types import AgentHasher, AgentSms
from ..repos import AgentRepo, User
from ..entities import BaseAgentCase
from ..exceptions import AgentDataTakenError
from ..models import RequestRepresesAgentsRegisterModel
from ...users.loggers.wrappers import user_changes_logger


class RepresesAgentsRegisterCase(BaseAgentCase):
    """
    Регистрация агента представителем агентства
    """
    sms_event_slug = "repres_registration_agent"

    def __init__(
        self,
        user_type: str,
        sms_class: Type[AgentSms],
        agent_repo: Type[AgentRepo],
        hasher: Callable[..., AgentHasher],
        password_generator: Callable[..., str],
        create_contact_service: CreateContactService,
        ensure_broker_tag_service: EnsureBrokerTagService,
        import_clients_task: Any,
        get_sms_template_service: GetSmsTemplateService,
    ) -> None:
        self.agent_repo: AgentRepo = agent_repo()
        self.agent_create = user_changes_logger(
            self.agent_repo.create, self, content="Создание агента"
        )
        self.agent_delete = user_changes_logger(
            self.agent_repo.delete, self, content="Удаление агента"
        )

        self.user_type: str = user_type
        self.hasher: AgentHasher = hasher()
        self.sms_class: Type[AgentSms] = sms_class
        self.password_generator: Callable[..., str] = password_generator
        self.create_contact_service: CreateContactService = create_contact_service
        self.ensure_broker_tag_service: EnsureBrokerTagService = ensure_broker_tag_service
        self.import_clients_task: Any = import_clients_task
        self.get_sms_template_service: GetSmsTemplateService = get_sms_template_service

    async def __call__(self, agency_id: int, payload: RequestRepresesAgentsRegisterModel) -> User:
        data: dict[str, Any] = payload.dict()
        phone: str = data["phone"]
        email: str = data["email"]

        # Удаляем запись помеченного удалённым агента из БД,
        # если есть такой с указанным телефоном или мылом
        filters = dict(type=UserType.AGENT, is_deleted=True)
        q_filters = [
            self.agent_repo.q_builder(or_filters=[dict(phone=phone), dict(email__iexact=email)])
        ]
        deleted_agent = await self.agent_repo.retrieve(filters=filters, q_filters=q_filters)
        if deleted_agent is not None:
            await self.agent_delete(deleted_agent)

        # Проверка на существование указанного агента в БД
        filters = dict(type=UserType.AGENT)
        q_filters = [
            self.agent_repo.q_builder(or_filters=[dict(phone=phone), dict(email__iexact=email)])
        ]
        agent: User = await self.agent_repo.retrieve(filters=filters, q_filters=q_filters)
        if agent:
            raise AgentDataTakenError

        one_time_password: str = self.password_generator()
        extra_data: dict[str, Any] = dict(
            is_approved=True,
            type=self.user_type,
            agency_id=agency_id,
            one_time_password=self.hasher.hash(one_time_password),
        )
        data.update(extra_data)
        agent: User = await self.agent_create(data=data)

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

        _, tags = await self.create_contact_service(agent=agent)
        setattr(agent, "tags", tags)
        await self.ensure_broker_tag_service(agent=agent)

        agent: User = await self.agent_repo.retrieve(filters=filters, q_filters=q_filters)
        self.import_clients_task.delay(agent_id=agent.id)

        return agent
