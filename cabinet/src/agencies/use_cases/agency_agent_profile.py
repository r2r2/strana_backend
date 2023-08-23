from typing import Any, Type

from src.agencies.entities import BaseAgencyCase
from src.agencies.exceptions import AgentAgencyNotFoundError
from src.agencies.repos import Agency
from src.agents.repos import AgentRepo
from src.users.repos import User


class GetAgencyForAgentProfile(BaseAgencyCase):
	"""Кейс получения профиля агентства для агента"""
	
	def __init__(
			self,
			agent_repo: Type[AgentRepo],
	):
		self.agent_repo = agent_repo()
	
	async def __call__(self, agent_id: int):
		filters = dict(id=agent_id)
		agent: User = await self.agent_repo.retrieve(
			filters=filters,
			prefetch_fields=["agency"]
		)
		agency: Agency = agent.agency
		if not agency:
			raise AgentAgencyNotFoundError
		return agency
