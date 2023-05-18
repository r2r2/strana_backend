from django.db.models import Q
from datetime import date
from .api import DvizhApiService
from projects.models import Project
from mortgage.models import Bank, OfferPanel
from mortgage.constants import DvizhProgramType
from rest_framework.exceptions import ValidationError
from .serializers import ProjectDvizhSerializer, BankDvizhSerializer, OfferDvizhSerializer


def update_dvizh_data() -> None:
    api = DvizhApiService()
    project_data_list = api.get_complexes()
    for project_data in project_data_list:
        name = project_data.pop("name")
        project_instance = Project.objects.filter(name__icontains=name.split("/")[-1]).last()
        if not project_instance:
            continue
        project_serializer = ProjectDvizhSerializer(instance=project_instance, data=project_data)
        project_serializer.is_valid(True)
        project_serializer.save()
    projects = (
        Project.objects
        .filter(dvizh_uuid__isnull=False)
        .annotate_flats_prices()
        .exclude(min_flat_price_penny__isnull=True)
    )
    for project in projects:
        bank_data_list = api.get_banks_complex(project.dvizh_uuid)
        for data in bank_data_list:
            bank_data = data["bank"]
            bank_instance = Bank.objects.filter(name=bank_data["name"]).last()
            if bank_instance and bank_instance.updated.date() == date.today():
                continue
            bank_serializer = BankDvizhSerializer(instance=bank_instance, data=bank_data)
            bank_serializer.is_valid(True)
            bank_serializer.save()

    all_offers = []
    all_banks = Bank.objects.filter(dvizh_id__isnull=False)
    for project in projects:
        for mortgage_type in DvizhProgramType.choices:
            for agenda_type in ["primary_housing", "commercial_mortgage"]:
                for price_type in ["min", "avg", "max"]:
                    offer_data_list = api.get_offers(
                        complex_id=project.dvizh_id,
                        mortgage_type=mortgage_type[0],
                        agenda_type=agenda_type,
                        price=getattr(project, f"{price_type}_flat_price_penny")
                    )
                    for offer_data in offer_data_list:

                        offer_id = offer_data.pop("id")
                        all_offers.append(offer_id)
                        offer_data.update(dict(
                            program_type=mortgage_type[0],
                            agenda_type=agenda_type,
                            city=project.city_id,
                        ))
                        offer_serializer = OfferDvizhSerializer(
                            data=offer_data
                        )
                        try:
                            offer_serializer.is_valid(True)
                        except ValidationError as e:
                            continue
                        validate_offer_data = offer_serializer.validated_data

                        offer_instance = OfferPanel.objects.filter(**validate_offer_data).last()
                        if offer_instance:
                            offer_serializer.instance = offer_instance
                        offer_instance = offer_serializer.save()
                        offer_instance.projects.add(project)
                        old_ids = offer_instance.dvizh_ids
                        if offer_id not in old_ids:
                            old_ids.append(offer_id)
                            offer_instance.dvizh_ids = old_ids
                            offer_instance.save()
    (
        OfferPanel.objects
        .exclude(
            Q(dvizh_ids__overlap=all_offers)|
            Q(dvizh_ids=[])
        )
        .update(is_active=False)
    )
