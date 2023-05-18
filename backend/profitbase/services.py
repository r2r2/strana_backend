from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta

from buildings.models import Building
from projects.models import Project
from properties.models import Property, SpecialOffer
from request_forms.constants import RequestType
from request_forms.models import Manager

from . import logger
from .api import ProfitBaseAPI
from .serializers import (BuildingProfitBaseSerializer,
                          ProjectProfitBaseSerializer,
                          PropertyProfitBaseSerializer,
                          SpecialOfferProfitBaseSerializer)
from .utils import parse_bool


class ProfitBaseService:
    """Сервисный слой синхронизации с ProfitBase."""
    def __init__(self):
        self.api = ProfitBaseAPI()
        self.project_data_list = self.api.get_projects()
        self.close_sync_ids = Project.objects.filter(close_sync=True).values_list("id", flat=True)

    def update_projects(self):
        """Обновление данных о жилых комплексах."""
        logger.info("Starting projects import ")
        project_data_list = self.api.get_projects()
        close_sync_ids = Project.objects.filter(close_sync=True).values_list("id", flat=True)
        for project_data in project_data_list:
            if project_data["id"] in close_sync_ids:
                continue
            project = Project.objects.filter(id=project_data["id"]).first()
            project_serializer = ProjectProfitBaseSerializer(instance=project, data=project_data)
            project_serializer.is_valid(True)
            project_serializer.save()

    def update_buildings(self):
        """Обновление данных о домах."""
        from .tasks import update_realty_for_project

        logger.info("Starting buildings import ")
        building_data_list = self.api.get_houses()
        close_sync_ids = Project.objects.filter(close_sync=True).values_list("id", flat=True)
        for building_data in building_data_list:
            development_end_quarter = building_data.pop("developmentEndQuarter")
            if building_data["projectId"] in close_sync_ids:
                continue
            if development_end_quarter:
                building_data.update(development_end_quarter)
            building = Building.objects.filter(id=building_data["id"]).first()
            if building is None:
                building_data.update({"is_active": False})
            building_serializer = BuildingProfitBaseSerializer(instance=building, data=building_data)
            building_serializer.is_valid(True)
            building_serializer.save()
        # создание или обновления помещений
        for project in self.project_data_list:
            if project["id"] in close_sync_ids:
                continue
            update_realty_for_project.delay(project["id"], self.api.access_token)

    def update_property_for_project(self, project_id: str, access_token: str = ""):
        """Обновление помещений только в одном проекте"""
        building_projects_mapping = dict(Building.objects.values_list("id", "project_id"))
        properties_data_list = self.api.get_properties(project_id)
        logger.info(f"Starting update project = {project_id}")
        for data in properties_data_list:
            try:
                if data["house_id"] not in building_projects_mapping.keys():
                    house_data = self.api.get_houses(data["house_id"])[0]
                    serializer = BuildingProfitBaseSerializer(data=house_data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    building_projects_mapping.update(
                        {serializer.instance.id: serializer.instance.project_id}
                    )
                data["project_id"] = building_projects_mapping[data["house_id"]]
                instance = Property.objects.filter(id=data["id"]).first()
                data.update({"floor_count_data": self.api.get_floors_count(data["house_id"])})
                if instance:
                    data["house_id"] = instance.building.id
                    data["plan_3d_1"] = instance.plan_3d_1
                data.update(data.pop("area", {}))
                serializer = PropertyProfitBaseSerializer(instance=instance, data=data)
                serializer.is_valid(True)
                serializer.save()
            except Exception as exc:
                logger.exception(
                    f"Error occurred during update. project {project_id}."
                )
        logger.info("Done.")

    def update_offers(self):
        """Обновление данных об акциях."""
        from .tasks import update_realty_for_project

        logger.info("Starting special offers import")
        special_offer_data_list = self.api.get_special_offers()
        for offer_data in special_offer_data_list:
            offer = SpecialOffer.objects.filter(id=offer_data["id"]).first()
            if offer and not offer.is_update_profit:
                continue
            if offer is None:
                if parse_bool(offer_data["discount"]["active"]) is False:
                    offer_data.update({"is_active": False})

            offer_serializer = SpecialOfferProfitBaseSerializer(instance=offer, data=offer_data)
            try:
                offer_serializer.is_valid(True)
            except Exception as e:
                logger.exception("Ошибка в ходе валидации данных с ProfitBase", offer_data)
            offer_serializer.save()
            if offer_data["id"] in (13428, 13466):
                offer.badge_label = offer_data["name"]
                offer.is_active = offer_data["discount"]["active"]
                offer.is_display = offer_data["discount"]["active"]
                offer.save()
        # создание или обновления помещений
        for project in self.project_data_list:
            if project["id"] in self.close_sync_ids:
                continue
            update_realty_for_project.delay(project["id"], self.api.access_token)


def notify_realty_update_managers() -> None:
    """Уведомление менеджеров по обновлению недвижимости, в случае, если обновление не происходит более 1 часа"""

    hour_ago = now() - timedelta(hours=1)
    recently_updated = (
        Property.objects.filter(update_time__gt=hour_ago).exclude(project__close_sync=True).exists()
    )

    if not recently_updated:
        managers = Manager.objects.filter(
            is_active=True, type_list__contains=[RequestType.REALTY_UPDATE]
        )
        managers = [x.email for x in managers]
        site = Site.objects.last()
        message = f"На сайте {site} нет обновленных квартир за последний час."
        subject = "Обновление недвижимости"

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.SERVER_EMAIL,
            recipient_list=managers,
        )
