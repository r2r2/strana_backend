from typing import Union

from src.booking.repos import BookingRepo


class BookingPropertyTypeSpecsCase:
    def __init__(self, booking_repo: type[BookingRepo]) -> None:
        self.booking_repo: BookingRepo = booking_repo()

    async def __call__(self, user_id: int) -> dict[str, list[dict[str, str]]]:
        return await self._prepare_to_response(
            await self._get_property_types_by_user_id(user_id)
        )

    async def _get_property_types_by_user_id(self, user_id: int) -> list[dict[str, str]]:
        filters = dict(user_id=user_id, active=True)
        _property_types = await (
            self.booking_repo.list(filters=filters)
            .prefetch_related("property__property_type")
            .distinct()
            .order_by("property__property_type__sort")
            .values(
                slug="property__property_type__slug",
                label="property__property_type__label",
                sort="property__property_type__sort",
                )
            )
        property_types = [property_type for property_type in _property_types if property_type["slug"] is not None]

        return property_types

    @staticmethod
    async def _prepare_to_response(
            list_property_types: list[dict[str, str]]
    ) -> dict[str, list[dict[str, str]]]:
        for property_types_dict in list_property_types:
            property_types_dict.pop("sort")
        return {
            "propertyTypes": list_property_types
        }
