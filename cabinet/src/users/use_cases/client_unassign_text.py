from typing import Union

from src.cities.repos import City
from src.notifications.exceptions import AssignClientTemplateNotFoundError
from src.notifications.repos import AssignClientTemplateRepo, AssignClientTemplate
from src.users.entities import BaseUserCase
from src.users.exceptions import UserNotFoundError
from src.users.repos import UserRepo, User


class UnassignTextCase(BaseUserCase):
    def __init__(
        self,
        user_repo: type[UserRepo],
        assign_client_template_repo: type[AssignClientTemplateRepo],
    ):
        self.user_repo = user_repo()
        self.assign_client_template_repo = assign_client_template_repo()

    async def __call__(self, user_id: int) -> AssignClientTemplate:
        user: User = await self.user_repo.retrieve(
            filters=dict(id=user_id),
            prefetch_fields=['interested_project', 'interested_project__city'],
        )
        if not user:
            raise UserNotFoundError

        if not user.interested_project:
            # Если нет проекта, то берем шаблон по умолчанию
            filters: dict[str, bool] = dict(default=True)
        else:
            filters: dict[str, Union[bool, City]] = dict(
                city=user.interested_project.city,
                default=False,
            )

        text_template: AssignClientTemplate = await self.assign_client_template_repo.retrieve(
            filters=dict(**filters),
        )
        if not text_template:
            raise AssignClientTemplateNotFoundError

        return text_template
