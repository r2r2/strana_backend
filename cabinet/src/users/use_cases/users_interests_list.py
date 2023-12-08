from typing import Type

from common import paginations
from src.users.entities import BaseUserCase
from src.users.models import ResponseInterestsList, SlugTypeChoiceFilters
from src.users.repos import InterestsRepo, UsersInterests
from src.properties.constants import PropertyStatuses


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
            related_fields=["property"],
        )
        user_interests_global_ids = self._get_sorted_unique_global_ids(user_interests=user_interests)

        # пагинируем отсортированный список global_ids вручную из-за кастомной сортировки
        if pagination.start and pagination.end:
            paginated_user_interests_global_ids = user_interests_global_ids[pagination.start:pagination.end]
        else:
            paginated_user_interests_global_ids = user_interests_global_ids

        return ResponseInterestsList(
            result=paginated_user_interests_global_ids,
            count=len(user_interests_global_ids),
            page_info=pagination(count=len(user_interests_global_ids)),
        )

    def _get_sorted_unique_global_ids(self, user_interests: list[UsersInterests]) -> list[str]:
        """
        Используем кастомную сортировку по статусам и удаляем дубли квартир из избранного.
        """

        user_interests_ordered_data = {
            PropertyStatuses.FREE: set(),
            PropertyStatuses.BOOKED: set(),
            PropertyStatuses.SOLD: set(),
        }
        for user_interest in user_interests:
            if user_interest.property.status is None:
                continue
            elif user_interest.property.status == PropertyStatuses.FREE:
                user_interests_ordered_data[PropertyStatuses.FREE].add(user_interest.property.global_id)
            elif user_interest.property.status == PropertyStatuses.BOOKED:
                user_interests_ordered_data[PropertyStatuses.BOOKED].add(user_interest.property.global_id)
            elif user_interest.property.status == PropertyStatuses.SOLD:
                user_interests_ordered_data[PropertyStatuses.SOLD].add(user_interest.property.global_id)

        global_ids = []
        for key, values in user_interests_ordered_data.items():
            global_ids.extend(values)

        return global_ids
