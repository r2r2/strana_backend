from typing import Type
# from health_check_sdk._response import HealthCheckResponse
from ..entities import BaseMaintenanceCase
from ..queries.health_checks import HealthCheckQueries
# from health_check_sdk.health_check import HealthCheck
# from ..checks import health_checks
# from ..checks.health_checks import NumberOfUnsuccessfulPayments


class HealthChecksCase(BaseMaintenanceCase):
    """
    Кейс информации по состоянию сервиса
    """

    def __init__(
        self,
        health_check_queries: HealthCheckQueries,
        # health_check: Type[HealthCheck],
    ) -> None:
        self.health_check_queries: HealthCheckQueries = health_check_queries
        # self.health_check: Type[HealthCheck] = health_check

    # async def __call__(self, content_type) -> HealthCheckResponse:
    #     return self.health_check.health_check(content_type, [NumberOfUnsuccessfulPayments])
