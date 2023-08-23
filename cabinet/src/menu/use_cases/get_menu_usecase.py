from typing import Type, Optional

from src.menu.entities import BaseMenuCase
from src.menu.repos import MenuRepo
from src.users.repos import UserRepo, User, UserRoleRepo


class GetMenuUseCase(BaseMenuCase):

    unauth_role_slug = "unauthorised"

    def __init__(
            self,
            menu_repos: Type['MenuRepo'],
            user_repos: Type['UserRepo'],
            role_repos: Type['UserRoleRepo'],
    ):
        self.menu_repos = menu_repos()
        self.user_repos = user_repos()
        self.role_repos = role_repos()

    async def __call__(self, city: str, user_id: Optional[int]) -> dict:
        user: User = await self.user_repos.retrieve(filters=dict(id=user_id), related_fields=['role'])

        if user:
            role = user.role.id
        else:
            role = (await self.role_repos.retrieve(filters=dict(slug=self.unauth_role_slug))).id
        filters = dict(cities__slug=city, roles__id=role)
        menu = await self.menu_repos.list(filters=filters, prefetch_fields=["roles", "cities"])
        return dict(result=menu)
