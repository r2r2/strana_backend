"""
Инициализация роутеров пока в таком виде из-за проблем с импортами
"""

from fastapi import APIRouter, FastAPI

def get_routers() -> list[APIRouter]:
    from src.tips.api import tips_router
    from src.pages.api import pages_router
    from src.cautions.api import caution_router
    from src.agencies.api import agencies_router
    from src.showtimes.api import showtimes_router
    from src.properties.api import properties_router
    from src.notifications.api import notifications_router
    from src.task_management.api import task_management_router
    from src.documents.api import documents_router, escrow_router
    from src.projects.api import projects_router, projects_router_v2
    from src.meetings.api import meeting_router
    from src.main_page.api import main_page_router

    # ToDo закомментированные роутеры не импортируются
    # from src.admins.api import admins_router
    # from src.agents.api import agents_router
    # from src.auth import auth_router
    # from src.booking.api import booking_router, fast_booking_router
    # from src.represes.api import represes_router
    # from src.users.api import manager_router, users_router, users_router_v2
    routers: list[APIRouter] = list()

    routers.append(documents_router)
    routers.append(escrow_router)
    routers.append(properties_router)
    routers.append(agencies_router)
    routers.append(pages_router)
    routers.append(notifications_router)
    routers.append(showtimes_router)
    routers.append(projects_router)
    routers.append(projects_router_v2)
    routers.append(caution_router)
    routers.append(task_management_router)
    routers.append(tips_router)
    routers.append(meeting_router)
    routers.append(main_page_router)

    # routers.append(auth_router)
    # routers.append(booking_router)
    # routers.append(fast_booking_router)
    # routers.append(agents_router)
    # routers.append(admins_router)
    # routers.append(users_router)
    # routers.append(manager_router)
    # routers.append(represes_router)
    # routers.append(users_router_v2)
    return routers


def initialize_routers(application: FastAPI) -> None:

    for router in get_routers():
        application.include_router(router)
