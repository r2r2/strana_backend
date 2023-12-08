from asyncio import Task
from typing import Any, Callable, Type

from src.agents.entities import BaseAgentCase
from src.agents.repos import AgentRepo
from src.agents.types import AgentEmail
from src.users.repos import User
from src.notifications.services import GetEmailTemplateService
from common.schemas import UrlEncodeDTO
from common.utils import generate_notify_url


class AgentResendLetterCase(BaseAgentCase):
	"""Повторная отправка письма на подтверждение почты"""
	mail_event_slug: str = "agent_confirm_email"
	common_link_route_template: str = "/confirm/agents/confirm_email"
	
	def __init__(
			self,
			email_class: Type[AgentEmail],
			site_config: dict[str, Any],
			token_creator: Callable[[int], str],
			agent_repo: Type[AgentRepo],
			get_email_template_service: GetEmailTemplateService,
	):
		self.email_class = email_class
		self.site_host: str = site_config["site_host"]
		self.token_creator: Callable[[int], str] = token_creator
		self.agent_repo: AgentRepo = agent_repo()
		self.get_email_template_service: GetEmailTemplateService = get_email_template_service
	
	async def __call__(self, agent_id: int) -> Any:
		agent: User = await self.agent_repo.retrieve(filters=dict(id=agent_id))
		token = self.token_creator(agent.id)
		self._send_confirm_email(agent=agent, token=token),
	
	async def _send_confirm_email(self, agent: User, token: str) -> Task:
		# copied from precess_register
		url_data: dict[str, Any] = dict(
			host = self.site_host,
			route_template = self.common_link_route_template,
			query_params = dict(
				q = token,
				p = agent.email_token,
			)
		)
		url_dto: UrlEncodeDTO = UrlEncodeDTO(**url_data)
		confirm_link: str = generate_notify_url(url_dto=url_dto)
		email_notification_template = await self.get_email_template_service(
			mail_event_slug=self.mail_event_slug,
			context=dict(confirm_link=confirm_link),
		)

		if email_notification_template and email_notification_template.is_active:
			email_options: dict[str, Any] = dict(
				topic=email_notification_template.template_topic,
				content=email_notification_template.content,
				recipients=[agent.email],
				lk_type=email_notification_template.lk_type.value,
				mail_event_slug=email_notification_template.mail_event_slug,
			)
			email_service: AgentEmail = self.email_class(**email_options)
			return email_service.as_task()
