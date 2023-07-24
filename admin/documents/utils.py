import os
import requests
from http import HTTPStatus
from .models import AgencyAdditionalAgreementCreatingData, AdditionalAgreementTemplate, AgencyAdditionalAgreement

SITE_HOST = os.getenv("LK_SITE_HOST")
EXPORT_CABINET_KEY = os.getenv("EXPORT_CABINET_KEY", default="default_key")


def additional_agency_email_notify(notify_data):
    api_link = f"https://{SITE_HOST}/api/agencies/superuser/additional_agency_email_notify"
    payload = {'data': EXPORT_CABINET_KEY}

    try:
        response = requests.post(api_link, params=payload, json=notify_data)
    except Exception:
        return False

    if response.status_code == HTTPStatus.OK:
        return True
    return False


def create_additional_agreements(additionaL_data_id):
    additionaL_data = AgencyAdditionalAgreementCreatingData.objects.get(id=additionaL_data_id)
    agencies = additionaL_data.agencies.select_related("city")
    projects = additionaL_data.projects.select_related("city")

    additional_agreements_ids = []
    superuser_additional_notify_agency_email_data = []

    for agency in agencies:
        project_names = []

        for project in projects:
            additional_agreement_template = AdditionalAgreementTemplate.objects.filter(
                project=project,
                type=agency.type,
            ).first()
            if not additional_agreement_template:
                continue

            template_name = additional_agreement_template.template_name
            additional_agreement = AgencyAdditionalAgreement.objects.create(
                agency=agency,
                project=project,
                template_name=template_name,
                reason_comment=additionaL_data.reason_comment,
                creating_data=additionaL_data,
            )
            project_names.append(project.name)
            additional_agreements_ids.append(additional_agreement.id)

        superuser_additional_notify_agency_email_data.append(
            dict(
                agency_id=agency.id,
                project_names=project_names,
            )
        )

    return additional_agreements_ids, superuser_additional_notify_agency_email_data
