from typing import Union

from src.cities.repos import City
from src.notifications.exceptions import AssignClientTemplateNotFoundError
from src.notifications.repos import AssignClientTemplateRepo, AssignClientTemplate
from src.users.constants import UserAssignSlug
from src.users.entities import BaseUserCase
from src.users.services import GetAgentClientFromQueryService


class AssignUnassignTextCase(BaseUserCase):
    def __init__(
        self,
        assign_client_template_repo: type[AssignClientTemplateRepo],
        get_agent_client_service: GetAgentClientFromQueryService,
    ):
        self.assign_client_template_repo: AssignClientTemplateRepo = assign_client_template_repo()
        self.get_agent_client_service: GetAgentClientFromQueryService = get_agent_client_service

    async def __call__(self, slug: str, token: str, data: str) -> AssignClientTemplate:
        agent, client = await self.get_agent_client_service(token=token, data=data)

        if not client.interested_project:
            # Если нет проекта, то берем шаблон по умолчанию
            filters: dict[str, bool] = dict(default=True)
        else:
            filters: dict[str, Union[bool, City]] = dict(
                city=client.interested_project.city,
                default=False,
            )

        text_template = await self.assign_client_template_repo.retrieve(filters=filters)

        if not text_template:
            # Если нет проекта, то берем шаблон по умолчанию
            text_template: AssignClientTemplate = await self.assign_client_template_repo.retrieve(
                filters=dict(default=True),
            )

        template_format: dict[str, str] = dict(
            agent_name=agent.full_name,
            client_name=client.full_name,
        )

        if slug == UserAssignSlug.CONFIRMED:
            text_template.text = text_template.success_assign_text.format(**template_format)
        elif slug == UserAssignSlug.UNASSIGNED:
            text_template.text = text_template.success_unassign_text.format(**template_format)
        elif slug == UserAssignSlug.UNASSIGN:
            text_template.text = text_template.text.format(**template_format)

        return text_template
