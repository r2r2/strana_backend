from tortoise.queryset import QuerySet

from common.paginations import PagePagination
from ..entities import BaseAdditionalServiceCase
from ..repos import (
    AdditionalServiceTicketRepo as TicketRepo,
    AdditionalServiceTicket as Ticket,
    AdditionalServiceTemplatetRepo as TemplateRepo,
    AdditionalServiceTemplate as Template,
    AdditionalServiceGroupStatusRepo as GroupStatusRepo,
    AdditionalServiceGroupStatus as GroupStatus,
)


class TicketListCase(BaseAdditionalServiceCase):
    """
    Кейс получения списка категорий и услуг
    """

    TEMPLATE_SLUG: str = "service_list"
    CANCELED_TICKET_SLUG: str = "ticket_canceled"

    def __init__(
        self,
        ticket_repo: type[TicketRepo],
        template_repo: type[TemplateRepo],
        group_status_repo: type[GroupStatusRepo],
    ) -> None:
        self.ticket_repo: TicketRepo = ticket_repo()
        self.template_repo: TemplateRepo = template_repo()
        self.group_status_repo: GroupStatusRepo = group_status_repo()

    async def __call__(
        self, category_id: int | None, user_id: int, pagination: PagePagination
    ) -> dict:
        filters: dict = dict(user_id=user_id)
        if category_id:
            filters.update(service__category_id=category_id)
        qs_options: dict = dict(filters=filters)
        tickets_count_qs: QuerySet = self.ticket_repo.list(**qs_options)
        qs_options.update(
            related_fields=["group_status", "service__category"],
            start=pagination.start,
            end=pagination.end,
            ordering="-id",
        )
        tickets_result_qs: QuerySet = self.ticket_repo.list(**qs_options)
        count: int = await tickets_count_qs.count()
        tickets: list[Ticket] = await tickets_result_qs
        template: Template = await self.template_repo.retrieve(
            filters=dict(slug=self.TEMPLATE_SLUG)
        )
        available_group_statuses: list[GroupStatus] = await self.group_status_repo.list(
            excluded=dict(slug=self.CANCELED_TICKET_SLUG)
        )
        ticket_result: dict = dict(
            count=count,
            result=tickets,
            page_info=pagination(count=count),
            template=template,
            statuses=available_group_statuses,
        )
        return ticket_result
