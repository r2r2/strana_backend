# pylint: disable=no-member
from asyncio import create_task, sleep
from datetime import datetime, timedelta
from typing import Any, Callable, Optional, Type, Union

from celery.app.task import Task
from pytz import UTC
from src.agents.tasks import import_clients_task
from src.users import constants as users_constants
from src.users.loggers.wrappers import user_changes_logger

from ..constants import UserType
from ..entities import BaseProcessLoginCase, BaseUserException
from ..exceptions import (UserNotApprovedError, UserNotFoundError,
                          UserWasDeletedError, UserWrongPasswordError)
from ..models import RequestProcessLoginModel
from ..repos import User, UserRepo
from ..types import UserHasher, UserSession
from .agents_user_login_cases import AbstractHandler


class ProcessLoginCase(BaseProcessLoginCase):
    """
    Процессинг входа
    """
    _NotFoundError: Type[BaseUserException] = UserNotFoundError
    _WrongPasswordError: Type[BaseUserException] = UserWrongPasswordError
    _NotApprovedError: Type[BaseUserException] = UserNotApprovedError
    _WasDeletedError: Type[BaseUserException] = UserWasDeletedError
    _import_clients_task: Task = import_clients_task

    def __init__(
        self,
        session: UserSession,
        user_repo: Type[UserRepo],
        auth_config: dict[str, Any],
        session_config: dict[str, Any],
        hasher: Callable[..., UserHasher],
        token_creator: Callable,
        login_handler: Optional[AbstractHandler] = None
    ) -> None:
        self.hasher: UserHasher = hasher()
        self.user_repo: UserRepo = user_repo()
        self.user_update = user_changes_logger(
            self.user_repo.update, self, content="Установка reset_time"
        )
        self.user_first_auth_update = user_changes_logger(
            self.user_repo.update, self, content="Обновление времени авторизации"
        )

        self._login_handler = login_handler

        self.session: UserSession = session
        self.token_creator: Callable = token_creator

        self.auth_key: str = session_config["auth_key"]
        self.password_time: int = auth_config["password_time"]
        self.password_settable_key: str = session_config["password_settable_key"]

        self.NotFoundError: Type[Exception] = self._NotFoundError
        self.WasDeletedError: Type[Exception] = self._WasDeletedError
        self.WrongPasswordError: Type[Exception] = self._WrongPasswordError
        self.NotApprovedError: Type[Exception] = self._NotApprovedError
        self.import_clients_task: Task = self._import_clients_task

    async def __call__(self, payload: RequestProcessLoginModel) -> dict[str, Any]:
        data: dict[str, Any] = payload.dict()
        email: str = data["email"]
        password: str = data["password"]
        admin_query = self.user_repo.retrieve(filters=dict(email__iexact=email, type=users_constants.UserType.ADMIN))
        repres_query = self.user_repo.retrieve(filters=dict(email__iexact=email, type=users_constants.UserType.REPRES))
        agent_query = self.user_repo.retrieve(filters=dict(email__iexact=email, type=users_constants.UserType.AGENT))

        user: User = await admin_query or await repres_query or await agent_query
        if not user:
            raise self.NotFoundError

        if payload.user_id and user.can_login_as_another_user:
            authorized_user = user
            user = await self.user_repo.retrieve(filters=dict(id=payload.user_id))
        else:
            authorized_user = None

        if not user.auth_first_at:
            await self.user_first_auth_update(user=user, data=dict(auth_first_at=datetime.now(tz=UTC)))

        if self._login_handler:
            self._login_handler.handle(user=user)

        if user.is_deleted or (authorized_user and authorized_user.is_deleted):
            raise self.WasDeletedError
        if user.one_time_password:
            if self.hasher.verify(password, user.one_time_password):
                self.session[self.password_settable_key]: int = user.id
                await self.session.insert()
                data: dict[str, Any] = dict(
                    reset_time=datetime.now(tz=UTC) + timedelta(minutes=self.password_time)
                )
                await self.user_update(user, data=data)
                create_task(self._remove_change_password_permission())
                token: dict[str, Any] = dict(type=None, token=None)
            else:
                raise self.WrongPasswordError
        else:
            if not self.hasher.verify(
                password,
                user.password if not authorized_user else authorized_user.password,
            ):
                raise self.WrongPasswordError
            if not user.is_approved:
                raise self.NotApprovedError
            extra: dict[str, Any] = dict(agency_id=user.agency_id, amocrm_id=user.amocrm_id)
            if user.agency_id:
                agency = await user.agency
                extra.update(agency_amocrm_id=agency.amocrm_id)

            token: dict[str, Any] = self.token_creator(subject_type=user.type.value, subject=user.id, extra=extra)
            token["id"]: int = user.id
            token["role"]: str = user.type.value
            self.session[self.auth_key]: dict[str, str] = token
            await self.session.insert()

            user.is_ready_for_authorisation_by_superuser = False
            await user.save()

        await self._import_amocrm_hook(user)
        token["is_fired"] = user.is_fired
        await self.user_update(user, data=dict(auth_last_at=datetime.now(tz=UTC)))

        return token

    async def _remove_change_password_permission(self) -> bool:
        """remove"""
        await sleep(self.password_time * 60)
        set_id: Union[int, None] = await self.session.get(self.password_settable_key)
        if set_id is not None:
            await self.session.pop(self.password_settable_key)
        return True

    async def _import_amocrm_hook(self, user: User):
        if user.type == UserType.AGENT:
            self.import_clients_task.delay(user.id)
        elif user.type == UserType.REPRES:
            agents = await self.user_repo.list(filters=dict(agency_id=user.agency_id, type=UserType.AGENT))
            self.import_clients_task.delay(user.id)
            for agent in agents:
                agent: User
                self.import_clients_task.delay(agent.id)
