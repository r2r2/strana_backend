from typing import Type

from common import paginations
from src.users.constants import SlugType
from src.users.entities import BaseUserCase
from src.users.models import ResponseInterestsList, SlugTypeChoiceFilters
from src.users.repos import InterestsRepo, UsersInterests


class UsersInterestsListCase(BaseUserCase):
    def __init__(self, user_interests_repo: Type[InterestsRepo]):
        self.user_interests_repo: InterestsRepo = user_interests_repo()

    async def __call__(
            self,
            user_id: int,
            pagination: paginations.PagePagination,
            init_filters: SlugTypeChoiceFilters,
    ) -> ResponseInterestsList:
        """
        Get properties from user_interests
        """
        filters: dict = dict(user_id=user_id)
        if init_filters.slug:
            filters.update(slug=init_filters.slug.value)

        user_interests: list[UsersInterests] = await self.user_interests_repo.list(
            filters=filters,
            prefetch_fields=['property'],
            start=pagination.start,
            end=pagination.end,
        )
        global_ids: list[str] = [interest.property.global_id for interest in user_interests]
        count = len(global_ids)
        return ResponseInterestsList(result=global_ids, count=count, page_info=pagination(count=count))
