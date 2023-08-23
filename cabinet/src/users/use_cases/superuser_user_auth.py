import requests
from typing import Any, Type
from http import HTTPStatus

from ..entities import BaseUserCase
from ..models import RequestSuperuserLoginModel
from ..repos import UserRepo, User
from ..exceptions import WrongSuperuserAuthAsUserDataError


class SuperuserAuthAsUserCase(BaseUserCase):
    """
    Получение токена для авторизации суперюзера под выбранным пользователем по кукам админки.
    """
    check_superuser_auth_link: str = "https://{}/admin/check_superuser_auth"

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
        user_id: int,
        payload: RequestSuperuserLoginModel,
    ) -> dict[str, str]:
        user: User = await self.user_repo.retrieve(filters=dict(id=user_id))
        superuser_is_authicated: bool = await self.check_superuser_auth(session_id=payload.session_id)
        if not user or not superuser_is_authicated:
            raise WrongSuperuserAuthAsUserDataError

        extra: dict[str, Any] = dict(agency_id=user.agency_id)
        token: dict[str, Any] = self.token_creator(subject_type=user.type.value, subject=user.id, extra=extra)
        token["id"]: int = user.id
        token["role"]: str = user.type.value
        token["is_fired"] = user.is_fired
        return token

    async def check_superuser_auth(self, session_id: str):
        check_superuser_auth_link = self.check_superuser_auth_link.format(self.site_host)
        cookies = dict(sessionid=session_id)

        try:
            response = requests.get(check_superuser_auth_link, cookies=cookies)
        except requests.exceptions.RequestException:
            return False

        if response.status_code != HTTPStatus.OK:
            return False

        return True if response.json().get("is_superuser") else False
