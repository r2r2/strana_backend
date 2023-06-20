from typing import Union

from src.cities.repos import City
from src.notifications.entities import BaseNotificationCase
from src.notifications.exceptions import AssignClientTemplateNotFoundError
from src.notifications.repos import AssignClientTemplateRepo, AssignClientTemplate
from src.projects.exceptions import ProjectNotFoundError
from src.projects.repos import ProjectRepo, Project


class AssignSMSTextCase(BaseNotificationCase):
    def __init__(
        self,
        project_repo: type[ProjectRepo],
        assign_client_template_repo: type[AssignClientTemplateRepo],
    ):
        self.project_repo: ProjectRepo = project_repo()
        self.assign_client_template_repo: AssignClientTemplateRepo = assign_client_template_repo()

    async def __call__(self, project_id: int) -> AssignClientTemplate:
        project: Project = await self.project_repo.retrieve(
            filters=dict(id=project_id),
            related_fields=['city'],
        )
        if not project:
            raise ProjectNotFoundError

        filters: dict[str, Union[bool, City]] = dict(city=project.city)

        text_template = await self.assign_client_template_repo.retrieve(filters=filters)

        if not text_template:
            text_template: AssignClientTemplate = await self.assign_client_template_repo.retrieve(
                filters=dict(default=True),
            )
            if not text_template:
                raise AssignClientTemplateNotFoundError
            text_template.text_found = False

        return text_template
