import time
from copy import copy
from datetime import datetime, timedelta
from typing import Any, Type, Coroutine

import structlog
from common.amocrm import AmoCRM, amocrm
from common.amocrm.types import AmoLead
from config import tortoise_config, amocrm_config
from src.booking.repos import Booking, BookingRepo
from tortoise import Tortoise


class CloseOldBookings:
    """
    Закрытие старых сделок.
    """

    FIXATION_TASK_CHAIN_NAME = "Продление сделки"

    def __init__(self):
        self.booking_repo: BookingRepo = BookingRepo()
        self.amocrm_class: type[AmoCRM] = amocrm.AmoCRM
        self.logger = structlog.get_logger()

        self.orm_class: Type[Tortoise] = Tortoise
        self.orm_config: dict[str, Any] = copy(tortoise_config)
        self.orm_config.pop("generate_schemas", None)
        self.partition_limit: int = amocrm_config["partition_limit"]

    def __await__(self) -> Coroutine:
        return self().__await__()

    async def _close_leads(self, days_period, days_offset, debug) -> int:
        needed_close_leads = await self._get_leads(days_period, days_offset)
        if not debug:
            await self._update_amocrm_leads(needed_close_leads)
            await self._update_booking_data(needed_close_leads)

        self.logger.info(f"Закрыты: {[lead.id for lead in needed_close_leads]}")
        return len(needed_close_leads)

    async def __call__(self, _days_offset: str = '50', **kwargs) -> None:
        self.logger.info("Запущен скрипт для закрытия старых сделок")
        days_period: int = 3000  # т.к. для АМО нужны две даты
        days_offset = int(_days_offset)
        debug: bool = False

        closed_leads_counter = 0
        while True:
            new_leads_counter = await self._close_leads(days_period, days_offset, debug)
            closed_leads_counter += new_leads_counter
            self.logger.info(f"Закрыто старых сделок: {closed_leads_counter}")
            if new_leads_counter < self.partition_limit:
                break
        print(f"+++ Всего закрыто {closed_leads_counter} старых сделок +++")

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

        await self.orm_class.init(config=self.orm_config)
        await self.booking_repo.bulk_update(filters=filters, data=update_data)
        await self.orm_class.close_connections()

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
        days_period: На сколько дней от days_offset в прошлое искать сделки.
        days_offset: Сдвиг влево от текущего дня, т.е. сделки созданные более days_offset дней назад
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

            leads: list[AmoLead] = await amocrm.fetch_leads(
                lead_ids=[],
                created_at_range=created_at_range,
                pipeline_statuses=pipeline_statuses,
            )

        return leads
