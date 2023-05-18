from asyncio import Task
from typing import Any, Callable, Type

from src.agents.entities import BaseAgentCase
from src.agents.repos import AgentRepo
from src.agents.types import AgentEmail
from src.users.repos import User


class AgentResendLetterCase(BaseAgentCase):
	"""Повторная отправка письма на подтверждение почты"""
	agent_confirm_template: str = "src/agents/templates/confirm_email.html"
	confirm_link: str = "https://{}/confirm/agents/confirm_email?q={}&p={}"
	
	def __init__(
			self,
			email_class: Type[AgentEmail],
			site_config: dict[str, Any],
			token_creator: Callable[[int], str],
			agent_repo: Type[AgentRepo],
	):
		self.email_class = email_class
		self.site_host: str = site_config["site_host"]
		self.token_creator: Callable[[int], str] = token_creator
		self.agent_repo: AgentRepo = agent_repo()
	
	async def __call__(self, agent_id: int) -> Any:
		agent: User = await self.agent_repo.retrieve(filters=dict(id=agent_id))
		token = self.token_creator(agent.id)
		self._send_confirm_email(agent=agent, token=token),
	
	async def _send_confirm_email(self, agent: User, token: str) -> Task:
		# copied from precess_register
		confirm_link: str = self.confirm_link.format(self.site_host, token, agent.email_token)
		email_options: dict[str, Any] = dict(
			topic="Подтверждение почты",
			template=self.agent_confirm_template,
			recipients=[agent.email],
			context=dict(confirm_link=confirm_link),
		)
		email_service: AgentEmail = self.email_class(**email_options)
		return email_service.as_task()
