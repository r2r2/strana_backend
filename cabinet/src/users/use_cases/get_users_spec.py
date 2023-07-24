import random
from typing import Type, Any

from tortoise.query_utils import Q

from common.requests import GraphQLRequest
from config import backend_config
from src.booking.repos import BookingRepo
from src.cities.repos import CityRepo
from src.notifications.repos import ClientNotification
from src.users.entities import BaseUserCase
from src.users.repos import InterestsRepo, UserRepo


class GetUsersSpecs(BaseUserCase):
    query_type: str = "allGlobalFlats"
    query_name: str = "allGlobalFlats.graphql"
    query_directory: str = "/src/users/queries/"

    def __init__(
            self,
            users_interested_repos: Type[InterestsRepo],
            booking_repos: Type[BookingRepo],
            users_repo: Type[UserRepo],
            city_repos: Type[CityRepo],
            notifications_model: Type[ClientNotification],
            request_class: Type[GraphQLRequest],
            backend_config: backend_config
    ):
        self.users_interested_repos = users_interested_repos()
        self.users_repo = users_repo()
        self.booking_repos = booking_repos()
        self.city_repos = city_repos()
        self.notifications_model = notifications_model
        self.request_class: Type[GraphQLRequest] = request_class
        self.backend_config = backend_config
        self.login: str = backend_config["internal_login"]
        self.password: str = backend_config["internal_password"]
        self.backend_url: str = backend_config["url"] + backend_config["graphql"]

    async def __call__(self, user_id: int, city_slug: str):
        active_bookings = await self.booking_repos.list(filters=dict(user_id=user_id, active=True)).count()
        released_bookings = await self.booking_repos.list(filters=dict(user_id=user_id),
                                                          q_filters=[
                                                              Q(amocrm_signed=True) | Q(price_payed=True)]).count()
        interest = await self.users_interested_repos.list(filters=dict(user_id=user_id)).count()

        city = await self.city_repos.retrieve(filters=dict(slug=city_slug))

        manager_filters = dict(role__name="Менеджер", users_cities=city.id)
        managers = await self.users_repo.list(filters=manager_filters)

        notifications = await self.notifications_model.all().filter(user_id=user_id).count()

        request_data: dict[str, Any] = dict(url=self.backend_url,
                                            type=self.query_type,
                                            query_name=self.query_name,
                                            query_directory=self.query_directory,
                                            filters=(r'"Q2l0eVR5cGU6Mg=="', r'"price"')
                                            )

        async with self.request_class(**request_data) as response:
            response_data = response.data["edges"][0]["node"]["price"]

        return dict(active_bookings=active_bookings, completed_bookings=released_bookings, interests=interest,
                    notifications=notifications, min_property_price=int(response_data),
                    phone=managers[random.randint(0, len(managers) - 1)].phone)
