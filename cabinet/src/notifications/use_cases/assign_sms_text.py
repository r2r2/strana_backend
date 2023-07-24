from src.notifications.entities import BaseNotificationCase
from src.notifications.repos import AssignClientTemplateRepo, AssignClientTemplate
from src.projects.exceptions import ProjectNotFoundError
from src.projects.repos import ProjectRepo, Project


class AssignSMSTextCase(BaseNotificationCase):
    sms_event_slug = "assign_client"
    sms_event_slug_msk = "assign_client_msk"
    sms_event_slug_spb = "assign_client_spb"

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

        slug = self.sms_event_slug
        if project.city.slug == 'moskva':
            slug = self.sms_event_slug_msk
        elif project.city.slug == 'spb':
            slug = self.sms_event_slug_spb

        text_template: AssignClientTemplate = await self.assign_client_template_repo.retrieve(
            filters=dict(
                city=project.city,
                sms__sms_event_slug=slug,
                sms__is_active=True,
                is_active=True,
            ),
            related_fields=["sms"],
        )

        if text_template:
            text_template.text = text_template.sms.template_text
        else:
            text_template: AssignClientTemplate = await self.assign_client_template_repo.retrieve(
                filters=dict(default=True, is_active=True, sms__is_active=True),
                related_fields=["sms"],
            )
            if text_template:
                text_template.text = text_template.sms.template_text

        return text_template
