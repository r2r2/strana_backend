import json

from common.loggers.utils import get_difference_between_two_dicts
from ..repos import Agency, AgencyRepo
from ..entities import BaseAgencyCase


def agency_changes_logger(agent_change: AgencyRepo(), use_case: BaseAgencyCase, content: str):
    from src.agencies.tasks import create_agency_log_task
    """
    Логирование изменений агентства
    """

    async def _wrapper(agency: Agency = None, data: dict = None, filters: dict = None):
        agency_after, response_data = dict(), dict()
        agency_before = json.dumps(dict(agency), indent=4, sort_keys=True, default=str) if agency else dict()
        agency_difference = dict()
        error_data = None

        if data and filters:
            update_agency = agent_change(filters=filters, data=data)
        elif agency and data:
            update_agency = agent_change(model=agency, data=data)
        elif agency:
            update_agency = agent_change(model=agency)
        else:
            update_agency = agent_change(data=data)

        try:
            agency: Agency = await update_agency
            agency_id = agency.id if agency else None
            agency_after = json.dumps(dict(agency), indent=4, sort_keys=True, default=str) if agency else dict()
            agency_difference = get_difference_between_two_dicts(agency_before, agency_after)
        except Exception as error:
            error_data = str(error)
            agency_id = None

        log_data: dict = dict(
            state_before=agency_before,
            state_after=agency_after,
            state_difference=agency_difference,
            content=content,
            agency_id=agency_id,
            response_data=response_data,
            use_case=use_case.__class__.__name__,
            error_data=error_data,
        )

        await create_agency_log_task(log_data=log_data)

        return agency

    return _wrapper
