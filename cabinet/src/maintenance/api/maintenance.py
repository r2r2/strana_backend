from fastapi import APIRouter, Request, Response, status
from fastapi.responses import JSONResponse
# from health_check_sdk.health_check import HealthCheck
# from health_check_sdk._response import HealthCheckResponse
from ..queries.health_checks import HealthCheckQueries
from src.booking.repos import BookingPaymentsMaintenanceRepo
from src.users.repos import ClientCheckMaintenanceRepo, ClientAssignMaintenanceRepo
from ..use_cases.health_check import HealthChecksCase

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])


@router.get("/_health", status_code=status.HTTP_200_OK)
async def health(request: Request, response: Response):
    content_type = request.headers.get('Content-Type')
    resources = dict(
        booking_payments_maintenance_repo=BookingPaymentsMaintenanceRepo,
        client_check_maintenance_repo=ClientCheckMaintenanceRepo,
        client_assign_maintenance_repo=ClientAssignMaintenanceRepo,
    )
    health_check_queries = HealthCheckQueries(**resources)
    health_check_case = HealthChecksCase(
        health_check_queries=health_check_queries,
        # health_check=HealthCheck,
    )
    rsp = await health_check_case(content_type=content_type)
    print(rsp.headers)
    return JSONResponse(content=rsp.response_body)
