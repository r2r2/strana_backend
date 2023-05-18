from asyncio import Task
from typing import Any, Optional, Type

from config import site_config

from common.email import EmailService
from src.agreements.repos import AgencyAdditionalAgreement
from src.getdoc.repos import AdditionalAgreementTemplate
from src.agents.types import AgentEmail

from ..entities import BaseAgencyCase
from ..models.admin_create_additional import RequestAgencyAdditionalAgreementModel
from ..repos import Agency, AgencyRepo
from ..types import AdditionalAgreementTemplateRepo, AgencyAdditionalAgreementRepo


class AdminAgenciesCreateAdditionalAgreementCase(BaseAgencyCase):
    """
    Создание дополнительного соглашения
    """
    repres_email_template = "src/agencies/templates/create_new_additional_agreemets.html"
    link = "https://{}/documents"

    def __init__(
        self,
        email_class: Type[AgentEmail],
        agency_repo: Type[AgencyRepo],
        additional_agreement_template_repo: Type[AdditionalAgreementTemplateRepo],
        additional_agreement_repo: Type[AgencyAdditionalAgreementRepo],
    ) -> None:
        self._agency_repo: AgencyRepo = agency_repo()
        self._additional_agreement_template_repo: AdditionalAgreementTemplateRepo = additional_agreement_template_repo()
        self._additional_agreement_repo: Type[AgencyAdditionalAgreementRepo] = additional_agreement_repo()
        self.email_class: Type[AgentEmail] = email_class

    async def __call__(
        self,
        *,
        comment: int,
        agencies: list[RequestAgencyAdditionalAgreementModel],
    ) -> list[AgencyAdditionalAgreement]:
        # id всех созданных ДС
        additional_agreements_ids = []

        for agency_data in agencies:
            agency: Optional[Agency] = await self._agency_repo.retrieve(
                filters=dict(id=agency_data.agency_id),
                related_fields=["maintainer"]
            )
            if not agency:
                continue

            # наименование всех выбранных проектов агентства
            project_names = []
            for project_id in agency_data.project_ids:
                additional_agreement_template: Optional[AdditionalAgreementTemplate] = await \
                    self._additional_agreement_template_repo.retrieve(
                        filters=dict(
                            project_id=project_id,
                            type=agency.type.value
                        ),
                        related_fields=["project"]
                    )
                if not additional_agreement_template:
                    continue
                template_name = additional_agreement_template.template_name

                # сохранение названия проекта для дальнейшей отправки в письме
                project_names.append(additional_agreement_template.project.name)

                additional_agreement_id: AgencyAdditionalAgreement = await self._create_additional_agreement(
                    agency_id=agency_data.agency_id,
                    project_id=project_id,
                    template_name=template_name,
                    comment=comment
                )
                additional_agreements_ids.append(additional_agreement_id)

            if agency.maintainer and agency.maintainer.email:
                await self._send_repres_email(
                    recipients=[agency.maintainer.email],
                    project_names=project_names,
                    link=self.link.format(site_config["broker_site_host"]),
                )

        select_related = ["status", "agency"]
        additional_agreements: list[AgencyAdditionalAgreement] = await self._additional_agreement_repo.list(
            filters=dict(id__in=additional_agreements_ids),
            related_fields=select_related,
        )

        return additional_agreements

    async def _create_additional_agreement(
        self,
        *,
        agency_id: int,
        project_id: int,
        template_name: str,
        comment: str,
    ) -> AgencyAdditionalAgreement:
        """Создание дополнительного соглашения в базе"""
        additional_data = dict(
            agency_id=agency_id,
            project_id=project_id,
            template_name=template_name,
            reason_comment=comment,
        )
        additional_agreement: AgencyAdditionalAgreement = await self._additional_agreement_repo.create(
            data=additional_data
        )
        return additional_agreement.id

    async def _send_repres_email(
        self,
        recipients: list[str],
        **context
    ) -> Task:
        """
        Уведомляем всех представителей агентств о новых дополнительных соглашениях.
        @param recipients: list[str]
        @param context: Any (Контекст, который будет использоваться в шаблоне письма)
        @return: Task
        """
        project_names = context.get("project_names")
        topic = ("Добрый день! Было сформировано новое дополнительное соглашение " +
                f"к договорам по следующим проектам: {', '.join(project_names)}.")

        email_options: dict[str, Any] = dict(
            topic=topic,
            template=self.repres_email_template,
            recipients=recipients,
            context=context,
        )
        email_service: EmailService = self.email_class(**email_options)

        return email_service.as_task()
