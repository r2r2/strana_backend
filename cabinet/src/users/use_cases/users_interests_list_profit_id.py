import binascii
from typing import Type

from pydantic import ValidationError

from common import paginations
from common.utils import from_global_id
from src.users.entities import BaseUserCase
from src.properties.constants import PropertyStatuses
from src.users.models import SlugTypeChoiceFilters
from src.users.repos import UsersInterests, InterestsRepo

from ..models import PropertyData


class UsersInterestsListProfitIdCase(BaseUserCase):
    """
    Get properties from user_interests
    """
    correct_property_types: list = [
        "GlobalFlatType",
        "GlobalPantryType",
        "GlobalParkingSpaceType",
        "GlobalCommercialSpaceType",
    ]

    def __init__(self, user_interests_repo: Type[InterestsRepo]):
        self.user_interests_repo: InterestsRepo = user_interests_repo()

    async def __call__(
        self,
        user_id: int,
        pagination: paginations.PagePagination,
        init_filters: SlugTypeChoiceFilters,
    ) -> dict:
        filters: dict = dict(user_id=user_id)
        if init_filters.slug:
            filters.update(slug=init_filters.slug.value)

        user_interests: list[UsersInterests] = await self.user_interests_repo.list(
            filters=filters,
            related_fields=["property"],
        )
        user_interests_profitbase_ids = self._get_sorted_unique_profitbase_ids(user_interests=user_interests)

        # пагинируем отсортированный список profitbase_ids вручную из-за кастомной сортировки
        if pagination.start is not None and pagination.end is not None:
            paginated_user_interests_global_ids = user_interests_profitbase_ids[pagination.start:pagination.end]
        else:
            paginated_user_interests_global_ids = user_interests_profitbase_ids

        profitbase_ids_data = dict(
            result=paginated_user_interests_global_ids,
            count=len(user_interests_profitbase_ids),
            page_info=pagination(count=len(user_interests_profitbase_ids)),
        )
        return profitbase_ids_data

    def _get_sorted_unique_profitbase_ids(self, user_interests: list[UsersInterests]) -> list[str]:
        """
        Используем кастомную сортировку по статусам и удаляем дубли квартир из избранного.
        """

        user_interests_ordered_data = {
            PropertyStatuses.FREE: set(),
            PropertyStatuses.BOOKED: set(),
            PropertyStatuses.SOLD: set(),
        }
        for user_interest in user_interests:
            profitbase_id = (
                self._get_profitbase_id(global_id=user_interest.property.global_id)
                if not user_interest.property.profitbase_id else user_interest.property.profitbase_id
            )
            if (
                profitbase_id is None
                or user_interest.property.status is None
                or not self._check_global_id_is_correct(user_interest.property.global_id)
            ):
                continue
            elif user_interest.property.status == PropertyStatuses.FREE:
                user_interests_ordered_data[PropertyStatuses.FREE].add(
                    PropertyData(profitbase_id=profitbase_id, global_id=user_interest.property.global_id)
                )
            elif user_interest.property.status == PropertyStatuses.BOOKED:
                user_interests_ordered_data[PropertyStatuses.BOOKED].add(
                    PropertyData(profitbase_id=profitbase_id, global_id=user_interest.property.global_id)
                )
            elif user_interest.property.status == PropertyStatuses.SOLD:
                user_interests_ordered_data[PropertyStatuses.SOLD].add(
                    PropertyData(profitbase_id=profitbase_id, global_id=user_interest.property.global_id)
                )

        profitbase_ids = []
        for key, values in user_interests_ordered_data.items():
            profitbase_ids.extend(values)

        return profitbase_ids

    def _get_profitbase_id(self, global_id: str) -> int | None:
        try:
            profitbase_id = int(from_global_id(global_id)[1])
        except (binascii.Error, UnicodeDecodeError, ValidationError, ValueError):
            profitbase_id = None
        return profitbase_id

    def _check_global_id_is_correct(self, global_id: str) -> bool:
        try:
            property_type, _ = from_global_id(global_id)
            return True if property_type in self.correct_property_types else False
        except (binascii.Error, UnicodeDecodeError, ValidationError, ValueError):
            return False
