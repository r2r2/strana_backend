# pylint: disable-all
from typing import Type

from fastapi import APIRouter
from tortoise import Model


def get_routers() -> list[APIRouter]:
    from src.admins.api import admins_router
    from src.agencies.api import agencies_router
    from src.agents.api import agents_router
    from src.auth import auth_router
    from src.booking.api import booking_router, fast_booking_router, booking_router_v2
    from src.documents.api import documents_router, escrow_router
    from src.notifications.api import notifications_router, templates_router
    from src.cautions.api import caution_router
    from src.task_management.api import task_management_router
    from src.pages.api import pages_router
    from src.projects.api import projects_router, projects_router_v2, projects_router_v3
    from src.buildings.api import buildings_router
    from src.properties.api import properties_router
    from src.favourites.api import favourites_router, favourites_router_v2
    from src.represes.api import represes_router
    from src.showtimes.api import showtimes_router
    from src.tips.api import tips_router
    from src.users.api import customers_router, manager_router, users_router, users_router_v2, user_dashboard_router
    from src.meetings.api import meeting_router
    from src.cities.api import cities_router
    from src.events.api import event_router, calendar_router
    from src.menu.api import menu_router
    from src.dashboard.api import dashboard_router
    from src.main_page.api import main_page_router
    from src.additional_services.api import add_services_router
    from src.events_list.api import events_list_router
    from src.feature_flags.api import feature_flags_router
    from src.commercial_offers.api import offers_router
    from src.news.api import news_router
    from src.mortgage.api import mortgage_router
    from src.maintenance.api import maintenance_router

    routers: list[APIRouter] = list()

    routers.append(tips_router)
    routers.append(auth_router)
    routers.append(users_router)
    routers.append(manager_router)
    routers.append(agents_router)
    routers.append(customers_router)
    routers.append(booking_router)
    routers.append(booking_router_v2)
    routers.append(fast_booking_router)
    routers.append(represes_router)
    routers.append(documents_router)
    routers.append(escrow_router)
    routers.append(properties_router)
    routers.append(favourites_router)
    routers.append(favourites_router_v2)
    routers.append(agencies_router)
    routers.append(pages_router)
    routers.append(notifications_router)
    routers.append(templates_router)
    routers.append(admins_router)
    routers.append(showtimes_router)
    routers.append(projects_router)
    routers.append(projects_router_v2)
    routers.append(projects_router_v3)
    routers.append(buildings_router)
    routers.append(users_router_v2)
    routers.append(user_dashboard_router)
    routers.append(caution_router)
    routers.append(task_management_router)
    routers.append(meeting_router)
    routers.append(cities_router)
    routers.append(event_router)
    routers.append(calendar_router)
    routers.append(menu_router)
    routers.append(dashboard_router)
    routers.append(main_page_router)
    routers.append(add_services_router)
    routers.append(events_list_router)
    routers.append(feature_flags_router)
    routers.append(offers_router)
    routers.append(news_router)
    routers.append(mortgage_router)
    routers.append(maintenance_router)

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
