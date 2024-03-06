from functools import wraps
from typing import Callable, Coroutine, Any

from src.users.models import RequestUsersCheckModel, RequestAssignClient
from .repos.client_assign_maintenance import ClientAssignMaintenanceRepo
from .repos.client_check_maintenance import ClientCheckMaintenanceRepo
from .repos.user import UserRepo

from tortoise import Model


def check_maintenance(method: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
    @wraps(method)
    async def wrapper(
        self,
        payload: RequestUsersCheckModel,
        agent_id: int | None = None,
        agency_id: int | None = None,
        user_id: int | None = None,
    ) -> Model:
        if agent_id:
            filters: dict[str: Any] = dict(id=agent_id)
        else:
            filters: dict[str: Any] = dict(agency_id=agency_id)
        broker_amocrm_id = await UserRepo().retrieve(filters=filters).values_list("amocrm_id", flat=True)
        error = None
        successful = True
        try:
            return await method(self, payload, agent_id, agency_id, user_id)
        except Exception as e:
            error = e
            successful = False
        finally:
            data = dict(
                client_phone=payload.phone,
                successful_check=successful,
                broker_amocrm_id=broker_amocrm_id,
            )
            await ClientCheckMaintenanceRepo().create(data=data)
            if error:
                raise error
    return wrapper


def assign_maintenance(method: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
    @wraps(method)
    async def wrapper(
        self,
        payload: RequestAssignClient,
        agent_id: int | None = None,
        repres_id: int | None = None,
    ) -> Model:
        broker_id = agent_id or repres_id
        filters: dict[str: Any] = dict(id=broker_id)
        broker_amocrm_id = await UserRepo().retrieve(filters=filters).values_list("amocrm_id", flat=True)
        error = None
        successful = True
        try:
            return await method(self, payload, agent_id, repres_id)
        except Exception as e:
            error = e
            successful = False
        finally:
            data = dict(
                client_phone=payload.phone,
                successful_assign=successful,
                broker_amocrm_id=broker_amocrm_id,
            )
            await ClientAssignMaintenanceRepo().create(data=data)
            if error:
                raise error
    return wrapper
