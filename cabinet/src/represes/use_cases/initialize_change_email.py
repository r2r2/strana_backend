from secrets import token_urlsafe
from typing import Type, Any, Callable

from . import BaseProceedEmailChanges
from ..repos import RepresRepo, User
from ..models import RequestInitializeChangeEmail
from ..exceptions import RepresNotFoundError, RepresEmailTakenError
from ..types import RepresEmail
from ...users.loggers.wrappers import user_changes_logger
from src.notifications.services import GetEmailTemplateService


class InitializeChangeEmailCase(BaseProceedEmailChanges):
    """
    Обновление почты агентом
    """
    mail_event_slug = "repres_change_email"

    def __init__(
        self,
        user_type: str,
        repres_repo: Type[RepresRepo],
        site_config: dict[str, Any],
        email_class: Type[RepresEmail],
        token_creator: Callable[[int], str],
        get_email_template_service: GetEmailTemplateService,
    ) -> None:
        self.repres_repo: RepresRepo = repres_repo()
        self.repres_update = user_changes_logger(
            self.repres_repo.update, self, content="Обновление почты представителя"
        )
        self.user_type: str = user_type
        self.email_class: Type[RepresEmail] = email_class
        self.token_creator: Callable[[int], str] = token_creator
        self.site_host: str = site_config["site_host"]
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service

    async def __call__(self, repres_id: int, payload: RequestInitializeChangeEmail) -> User:
        email = payload.email
        filters: dict[str, Any] = dict(id=repres_id, is_deleted=False, type=self.user_type)
        repres: User = await self.repres_repo.retrieve(filters=filters)
        if not repres:
            raise RepresNotFoundError
        filters: dict[str, Any] = dict(email__iexact=email)
        user: User = await self.repres_repo.retrieve(filters=filters)
        if user and user.id != repres.id:
            raise RepresEmailTakenError
        data = dict()
        data["change_email"]: str = email
        data["change_email_token"]: str = token_urlsafe(32)
        email_token: str = self.token_creator(repres.id)
        repres: User = await self.repres_update(repres, data=data)
        await self._send_email(repres=repres, token=email_token)
        return repres
