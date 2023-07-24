from typing import Type

from common.paginations import PagePagination
from src.menu.entities import BaseMenuCase
from src.menu.repos import MenuRepo
from src.users.repos import UserRepo, User


class GetMenuUseCase(BaseMenuCase):

    def __init__(
            self,
            menu_repos: Type['MenuRepo'],
            user_repos: Type['UserRepo']
    ):
        self.menu_repos = menu_repos()
        self.user_repos = user_repos()

    async def __call__(self, city: str, user_id: int, pagination: PagePagination) -> dict:
        user: User = await self.user_repos.retrieve(filters=dict(id=user_id), related_fields=['role'])

        filters = dict(cities__slug=city, roles__id=user.role.id)
        menu = await self.menu_repos.list(filters=filters, start=pagination.start, end=pagination.end,
                                          prefetch_fields=["roles", "cities"])
        counted = await self.menu_repos.list(filters=filters).count()
        return dict(count=counted, result=menu, page_info=pagination(count=counted))
