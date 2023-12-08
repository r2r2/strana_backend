import time
from datetime import datetime, timedelta
from typing import Any

import structlog

from common.amocrm import AmoCRM

from common.amocrm.types import AmoLead
from src.booking.repos import Booking, BookingRepo


class CloseOldBookingCase:
    FIXATION_TASK_CHAIN_NAME = "Продление сделки"

    def __init__(
        self,
        booking_repo: type[BookingRepo],
        amocrm_class: type[AmoCRM],
    ):
        self.booking_repo: BookingRepo = booking_repo()
        self.amocrm_class: type[AmoCRM] = amocrm_class
        self.logger = structlog.get_logger()

    async def __call__(self, days_period: int, days_offset: int, debug: bool) -> list[AmoLead]:
        self.logger.info("Запущен скрипт для закрытия старых сделок")
        needed_close_leads = await self._get_leads(days_period, days_offset)
        self.logger.info(f"Старых сделок для закрытия - {len(needed_close_leads)}")

        if not debug:
            await self._update_amocrm_leads(needed_close_leads)
            await self._update_booking_data(needed_close_leads)

        return needed_close_leads

    async def _update_booking_data(self, leads: list[AmoLead]) -> None:
        """
        Отвязывание всех сделок от агентов.
        Ставим статус ЗАКРЫТО и НЕ РЕАЛИЗОВАНО, active=False.
        """
        filters = dict(amocrm_id__in=[leads.id for leads in leads])
        update_data: dict[str, Any] = dict(
            agent_id=None,
            agency_id=None,
            amocrm_stage=Booking.stages.DDU_UNREGISTERED,
            amocrm_substage=Booking.substages.UNREALIZED,
            active=False,
        )
        await self.booking_repo.bulk_update(filters=filters, data=update_data)

    async def _update_amocrm_leads(self, leads: list[AmoLead]):
        """
        Обновить сделки в амо.
        Всем сделкам ставим статус "закрыто и не реализовано"
        """
        async with await self.amocrm_class() as amocrm:
            lead_options: dict[str, Any] = dict(
                status_id=amocrm.unrealized_status_id,
                lead_ids=[lead.id for lead in leads],
            )
            await amocrm.update_leads_v4(**lead_options)

    async def _get_leads(self, days_period, days_offset) -> list[AmoLead]:
        """
        Получение списка сделок требующих закрытия.
        """
        async with await self.amocrm_class() as amocrm:
            statuses_data = (
                (amocrm.PipelineIds.TYUMEN, amocrm.TMNStatuses),
                (amocrm.PipelineIds.MOSCOW, amocrm.MSKStatuses),
                (amocrm.PipelineIds.SPB, amocrm.SPBStatuses),
                (amocrm.PipelineIds.EKB, amocrm.EKBStatuses),
                (amocrm.PipelineIds.TEST, amocrm.TestStatuses),
            )
            pipeline_statuses = []
            for pipeline_status in statuses_data:
                pipeline_statuses.append((pipeline_status[0], pipeline_status[1].START))
                pipeline_statuses.append((pipeline_status[0], pipeline_status[1].ASSIGN_AGENT))
                pipeline_statuses.append((pipeline_status[0], pipeline_status[1].MAKE_APPOINTMENT))
                pipeline_statuses.append((pipeline_status[0], pipeline_status[1].MEETING))
                pipeline_statuses.append((pipeline_status[0], pipeline_status[1].MEETING_IN_PROGRESS))
                pipeline_statuses.append((pipeline_status[0], pipeline_status[1].MAKE_DECISION))
                pipeline_statuses.append((pipeline_status[0], pipeline_status[1].RE_MEETING))

            start_day = datetime.today() - timedelta(days=days_offset+days_period)
            start_unixtime = int(time.mktime(start_day.timetuple()))
            end_day = datetime.today() - timedelta(days=days_offset)
            end_unixtime = int(time.mktime(end_day.timetuple()))
            created_at_range: dict = {'from': start_unixtime, 'to': end_unixtime}

            leads: list[AmoLead] | None = await amocrm.fetch_leads(lead_ids=[], created_at_range=created_at_range,
                                                                   pipeline_statuses=pipeline_statuses)

        return leads
