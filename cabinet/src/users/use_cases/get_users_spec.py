import binascii
from typing import Type

from pydantic import ValidationError
from tortoise.expressions import Q

from common.calculator.calculator import CalculatorAPI
from common.calculator.exeptions import BaseCalculatorException
from common.utils import from_global_id
from common.backend import repos as backend_repos
from src.booking.repos import BookingRepo
from src.booking.utils import get_statuses_before_booking
from src.cities.repos import CityRepo
from src.notifications.repos import ClientNotification
from src.users.entities import BaseUserCase
from src.users.repos import InterestsRepo
from src.properties.constants import PropertyStatuses


class GetUsersSpecs(BaseUserCase):
    correct_property_types: list = [
        "GlobalFlatType",
        "GlobalPantryType",
        "GlobalParkingSpaceType",
        "GlobalCommercialSpaceType",
    ]

    def __init__(
            self,
            users_interested_repos: Type[InterestsRepo],
            booking_repos: Type[BookingRepo],
            city_repos: Type[CityRepo],
            notifications_model: Type[ClientNotification],
            calculator_class: CalculatorAPI,
            backend_properties_repo: type[backend_repos.BackendPropertiesRepo],
    ):
        self.users_interested_repos = users_interested_repos()
        self.booking_repos = booking_repos()
        self.city_repos = city_repos()
        self.notifications_model = notifications_model
        self.calculator_class: CalculatorAPI = calculator_class
        self.backend_properties_repo: backend_repos.BackendPropertiesRepo = backend_properties_repo()

    async def __call__(self, user_id: int, city_slug: str):
        booking_filters = dict(
            user_id=user_id,
            active=True,
            property_id__isnull=False,
            building_id__isnull=False,
            project_id__isnull=False,
            amocrm_status__id__not_in=get_statuses_before_booking(),
        )
        active_bookings = await self.booking_repos.count(filters=booking_filters)
        released_bookings = await self.booking_repos.count(filters=dict(user_id=user_id),
                                                          q_filters=[
                                                              Q(amocrm_signed=True) | Q(price_payed=True)])

        interests_filter = dict(user_id=user_id)
        interest_global_ids = await self.users_interested_repos.list(
            filters=interests_filter,
        ).distinct().values_list("property__global_id", flat=True)
        interest = await self._count_correct_interest_global_ids(interest_global_ids)

        city = await self.city_repos.retrieve(filters=dict(slug=city_slug))

        notifications = await self.notifications_model.all().filter(user_id=user_id).count()

        async with self.calculator_class as calculator:
            response = await calculator.get_loan_offers_spec(city.slug)

        if response.status != 200:
            raise BaseCalculatorException

        return dict(active_bookings=active_bookings, completed_bookings=released_bookings, interests=interest,
                    notifications=notifications, min_property_price=int(response.data["cost"]["range"]["min"]))

    async def _count_correct_interest_global_ids(self, interest_global_ids: list[str]) -> int:
        correct_interest_global_ids = []
        for interest_global_id in interest_global_ids:
            try:
                property_type, backend_property_id = from_global_id(interest_global_id)
                property_status_from_portal = await self._get_property_status_from_portal(
                    backend_property_id=int(backend_property_id),
                )
                if (
                    property_type in self.correct_property_types
                    and property_status_from_portal is not None
                    and property_status_from_portal == PropertyStatuses.FREE
                ):
                    correct_interest_global_ids.append(interest_global_id)
            except (binascii.Error, UnicodeDecodeError, ValidationError, ValueError):
                continue

        return len(correct_interest_global_ids)

    async def _get_property_status_from_portal(self, backend_property_id: int) -> int | None:
        backend_property = await self.backend_properties_repo.retrieve(filters=dict(id=backend_property_id))
        return backend_property.status if backend_property else None
