# pylint: disable-all
from typing import Type

from fastapi import APIRouter
from tortoise import Model


def get_routers() -> list[APIRouter]:
    from src.admins.api import admins_router
    from src.agencies.api import agencies_router
    from src.agents.api import agents_router
    from src.auth import auth_router
    from src.booking.api import booking_router, fast_booking_router
    from src.cautions.api import caution_router
    from src.documents.api import documents_router, escrow_router
    from src.notifications.api import notifications_router
    from src.cautions.api import caution_router
    from src.task_management.api import task_management_router
    from src.pages.api import pages_router
    from src.projects.api import projects_router, projects_router_v2
    from src.properties.api import properties_router
    from src.represes.api import represes_router
    from src.showtimes.api import showtimes_router
    from src.tips.api import tips_router
    from src.users.api import manager_router, users_router, users_router_v2
    from src.meetings.api import meeting_router
    from src.cities.api import cities_router

    routers: list[APIRouter] = list()

    routers.append(tips_router)
    routers.append(auth_router)
    routers.append(users_router)
    routers.append(manager_router)
    routers.append(agents_router)
    routers.append(booking_router)
    routers.append(fast_booking_router)
    routers.append(represes_router)
    routers.append(documents_router)
    routers.append(escrow_router)
    routers.append(properties_router)
    routers.append(agencies_router)
    routers.append(pages_router)
    routers.append(notifications_router)
    routers.append(admins_router)
    routers.append(showtimes_router)
    routers.append(projects_router)
    routers.append(projects_router_v2)
    routers.append(users_router_v2)
    routers.append(caution_router)
    routers.append(task_management_router)
    routers.append(meeting_router)
    routers.append(cities_router)

    return routers


class DBRouter:

    @staticmethod
    def get_connector(model: Type[Model]):
        """
        Try to found connector in model Metadata.
        Default connector - cabinet.
        """

        return getattr(model.Meta, 'app', 'cabinet')

    def db_for_read(self, model: Type[Model]):
        return self.get_connector(model)

    def db_for_write(self, model: Type[Model]):
        return self.get_connector(model)