import asyncio
import datetime
from typing import Type, Any

from pytz import UTC

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoElementTypes, AmoTaskTypes
from common.email import EmailService
from src.admins.repos import AdminRepo
from src.agencies.repos import Agency
from src.agents.types import AgentEmail, AgentSms
from src.notifications.services import GetEmailTemplateService
from src.users.constants import UserType
from src.users.entities import BaseUserCase
from src.users.exceptions import ConfirmClientAssignNotFoundError
from src.users.models import ResponseUnassignClient
from src.users.repos import User, ConfirmClientAssignRepo, ConfirmClientAssign
from src.users.services import GetAgentClientFromQueryService


class UnassignCase(BaseUserCase):
    mail_event_slug = "manager_unassign_case"
    task_message = 'Связаться: Позвонить клиенту, он нажал кнопку "Открепиться", проверь на случайность и ' \
                   'обязательно заполни резервный комментарий к задаче.'

    def __init__(
        self,
        admin_repo: Type[AdminRepo],
        confirm_client_assign_repo: Type[ConfirmClientAssignRepo],
        email_class: Type[AgentEmail],
        amocrm_class: Type[AmoCRM],
        sms_class: Type[AgentSms],
        get_email_template_service: GetEmailTemplateService,
        get_agent_client_service: GetAgentClientFromQueryService,
    ):
        self.admin_repo = admin_repo()
        self.get_agent_client_service: GetAgentClientFromQueryService = get_agent_client_service
        self.confirm_client_assign_repo: ConfirmClientAssignRepo = confirm_client_assign_repo()
        self.email_class: Type[AgentEmail] = email_class
        self.amocrm_class: Type[AmoCRM] = amocrm_class
        self.sms_class: Type[AgentSms] = sms_class
        self.get_email_template_service = get_email_template_service

        # note: временный ответственный, пока не известна логика получения
        self.responsible_manager_amocrm_id = 6541746

    async def __call__(self, token: str, data: str) -> ResponseUnassignClient:
        agent, client = await self.get_agent_client_service(token=token, data=data)
        await self._create_task_for_manager(client_amocrm_id=client.amocrm_id)

        filters = dict(type=UserType.ADMIN, receive_admin_emails=True)
        admins = await self.admin_repo.list(filters=filters)

        await asyncio.gather(
            self._send_manager_email(
                recipients=[admin.email for admin in admins],
                client_name=client.full_name,
                agent_name=agent.full_name
            ),
            self._set_unassigned_time(
                client=client,
                agent=agent,
                agency=agent.agency,
            )
        )
        return ResponseUnassignClient.from_orm(client)

    async def _send_manager_email(self, recipients: list[str], **context) -> asyncio.Task:
        """
        Уведомляем менеджера страны о закреплении клиента.
        @param recipients: list[str]
        @param context: Any (Контекст, который будет использоваться в шаблоне письма)
        @return: Task
        """
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.mail_event_slug,
            context=context,
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=recipients,
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: EmailService = self.email_class(**email_options)
            return email_service.as_task()

    async def _create_task_for_manager(self, client_amocrm_id: int):
        complete_till_datetime = datetime.datetime.now() + datetime.timedelta(days=2)

        async with await self.amocrm_class() as amocrm:
            await amocrm.create_task(
                element_id=client_amocrm_id,
                element_type=AmoElementTypes.CONTACT,
                task_type=AmoTaskTypes.CALL,
                text=self.task_message,
                complete_till=int(complete_till_datetime.timestamp()),
                responsible_user_id=self.responsible_manager_amocrm_id
            )

    async def _set_unassigned_time(self, client: User, agent: User, agency: Agency) -> None:
        """
        Устанавливаем время открепления клиента от агента.
        @param client: User
        @param agent: User
        @param agency: Agency
        @return: None
        """
        confirm_client: ConfirmClientAssign = await self.confirm_client_assign_repo.retrieve(
            filters=dict(client=client, agent=agent, agency=agency)
        )
        if not confirm_client:
            raise ConfirmClientAssignNotFoundError

        data: dict[str, Any] = dict(
            unassigned_at=datetime.datetime.now(tz=UTC)
        )
        await self.confirm_client_assign_repo.update(model=confirm_client, data=data)
