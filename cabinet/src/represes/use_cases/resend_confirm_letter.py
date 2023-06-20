from asyncio import Task
from typing import Any, Callable, Type

from src.represes.entities import BaseRepresCase
from src.represes.repos import RepresRepo
from src.represes.types import RepresEmail
from src.users.repos import User
from src.notifications.services import GetEmailTemplateService


class RepresResendLetterCase(BaseRepresCase):
	"""
	Повторная отправка письма на подтверждение почты
	"""

	mail_event_slug = "repres_confirm_email"
	confirm_link: str = "https://{}/confirm/represes/confirm_email?q={}&p={}"
	
	def __init__(
			self,
			email_class: Type[RepresEmail],
			site_config: dict[str, Any],
			token_creator: Callable[[int], str],
			repres_repo: Type[RepresRepo],
			get_email_template_service: GetEmailTemplateService,
	):
		self.email_class = email_class
		self.site_host: str = site_config["site_host"]
		self.token_creator: Callable[[int], str] = token_creator
		self.repres_repo: RepresRepo = repres_repo()
		self.get_email_template_service: GetEmailTemplateService = get_email_template_service
	
	async def __call__(self, agent_id: int) -> Any:
		repres: User = await self.repres_repo.retrieve(filters=dict(id=agent_id))
		token = self.token_creator(repres.id)
		self._send_confirm_email(repres=repres, token=token),
	
	async def _send_confirm_email(self, repres: User, token: str) -> Task:
		"""
		Отправка письма репрезу с просьбой подтверждения почты
		"""
		confirm_link: str = self.confirm_link.format(self.site_host, token, repres.email_token)
		email_notification_template = await self.get_email_template_service(
			mail_event_slug=self.mail_event_slug,
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
