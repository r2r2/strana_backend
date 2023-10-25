import requests
from typing import Any, Type
from http import HTTPStatus

from ..entities import BaseUserCase
from ..models import RequestSuperuserClientLoginModel
from ..repos import UserRepo, User
from ..exceptions import WrongSuperuserAuthAsUserDataError


class SuperuserAuthAsClientCase(BaseUserCase):
    """
    Получение токена для авторизации суперюзера под выбранным клиентом по кукам админки.
    """

    def __init__(
        self,
        token_creator: Any,
        user_repo: Type[UserRepo],
        site_config: dict[str, Any],
    ) -> None:
        self.token_creator: Any = token_creator
        self.user_repo: UserRepo = user_repo()
        self.site_host: str = site_config["site_host"]

    async def __call__(
        self,
        payload: RequestSuperuserClientLoginModel,
    ) -> dict[str, str]:
        user: User = await self.user_repo.retrieve(filters=dict(id=payload.client_id))
        if not user:
            raise WrongSuperuserAuthAsUserDataError

        extra: dict[str, Any] = dict(agency_id=user.agency_id)
        token: dict[str, Any] = self.token_creator(subject_type=user.type.value, subject=user.id, extra=extra)
        token["id"]: int = user.id
        token["role"]: str = user.type.value
        token["is_fired"] = user.is_fired

        await self.user_repo.update(model=user, data=dict(client_token_for_superuser=token.get("token")))
