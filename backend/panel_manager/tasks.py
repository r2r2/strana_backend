import json
import math
from celery.utils.log import get_task_logger

import requests
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.utils.timezone import now

from celery import shared_task
from infras.models import Infra, InfraType
from panel_manager.models import Meeting
from panel_manager.services import PanelManagerAmoCrm
from projects.models import Project

logger = get_task_logger(__name__)
YANDEX_MAPS_API_URL = "https://search-maps.yandex.ru/v1/"
PAGE_SIZE = 500


def request_map_objects_data(text, coords, area, page=0, count=PAGE_SIZE):
    params = {
        "apikey": "c94cedd1-8062-4fa8-aa67-e17990c1f867",
        "type": "biz",
        "lang": "ru_RU",
        "text": text,
        "ll": coords,  # центр области поиска
        "spn": area,  # размеры области поиска
        "rspn": 1,  # не искать за пределами области
        "results": count,
        "skip": PAGE_SIZE * page,
    }
    res = requests.get(YANDEX_MAPS_API_URL, params=params)
    res.raise_for_status()
    data = res.json()
    return data["features"]


def get_area_in_degrees(coords, area):
    """

    :type coords: str - "lat,lng", °
    :type area: str - "dlat,dlng", km
    """
    dlat, dlng = map(float, area.split(","))
    lat, lng = coords.split(",")
    lat = float(lat)

    dlat /= 111.134861111  # km -> °
    dlng /= 111.321377778 * math.cos(lat * math.pi / 180)

    return str(dlat) + "," + str(dlng)


def swap_coords(coords):
    return ",".join(reversed(coords.split(",")))


def get_map_objects_data(text, coords, area, count):
    area = get_area_in_degrees(coords, area)

    # lat,lng -> lng,lat
    coords = swap_coords(coords)
    area = swap_coords(area)

    page = 0
    objs = []
    while count > 0:
        rest_count = min(PAGE_SIZE, count)
        res = request_map_objects_data(text, coords, area, page, rest_count)
        if len(res) == 0:
            break
        objs.extend(res)
        page += 1
        count -= rest_count

    return objs


@shared_task(ignore_result=True)
def update_infra_objects():
    panel_projects_qs = Project.objects.filter(active=True).exclude(latitude=None)
    for panel_project in panel_projects_qs:
        update_project_infra(panel_project)


def update_project_infra(panel_project: Project):

    area = "5.0" + "," + "5.0"
    for infra_type in InfraType.objects.all():
        data = get_map_objects_data(
            infra_type.name, f"{panel_project.latitude},{panel_project.longitude}", area, 10
        )
        for item in data:
            lat, long = map(str, reversed(item["geometry"]["coordinates"]))

            Infra.objects.get_or_create(
                project=panel_project,
                type=infra_type,
                category=infra_type.category,
                name=item["properties"]["name"][:98],
                latitude=lat,
                longitude=long,
                show_in_panel=True,
                show_in_site=False,
                defaults={"description": item["properties"]["description"]},
            )


@shared_task(ignore_result=True)
def send_broshure(email: str, list_id_property: list):
    """Отправка email и списка id избранных помещений"""
    url = f'https://mr-panel.idacloud.ru/pdf/brochure?id={",".join(list_id_property)}&format=a4'
    response = requests.get(url)
    response.raise_for_status()
    subject = f"Выбранные_Помещения"
    connection = get_connection()
    mail = EmailMultiAlternatives(
        subject, subject, settings.EMAIL_HOST_USER, [email], connection=connection
    )
    mail.attach(
        filename=f"{subject}.pdf",
        content=response.content,
        mimetype="application/pdf",
    )
    mail.send()


@shared_task(ignore_result=True)
def process_meeting(meeting_id: str):
    """Обработка встречи после создания/изменения."""
    logger.warning("Start processing meeting")
    meeting = Meeting.objects.filter(pk=meeting_id).last()
    if not meeting:
        logger.error(f"Встреча с id {meeting_id} не найдена")
        return
    if meeting.project:
        Meeting.objects.filter(id=meeting.id).update(city=meeting.project.city)
    if meeting.datetime_end:
        meeting.send_brochure()
    if meeting.meeting_end_type:
        service = PanelManagerAmoCrm()
        service.update_meeting_in_crm(meeting=meeting)
        service.create_update_tasks(meeting=meeting)
        service.create_note(
            lead_id=meeting.id_crm, text=f"О чем договорились: {meeting.comment}"
        )

@shared_task(ignore_result=True)
def process_webhook(data: dict, site_id: int=None):
    """Обработка данных, полученных из вебхука AmoCRM."""
    try:
        PanelManagerAmoCrm().processing_webhook(data, site_id)
    except Exception as e:
        logger.exception("Ошибка обработки данных встречи")
