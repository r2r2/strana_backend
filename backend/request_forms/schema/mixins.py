from datetime import timedelta
from graphene import List, Boolean

from django.conf import settings
from django.utils.timezone import now

from projects.models import Project
from common.schema import ErrorType
from common.utils import collect_form_errors
from .inputs import NameAndPhoneInput
from ..forms import NamePhoneAndProjectForm
from ..services import RequestEmail


class RequestMutationMixin:
    """
    Миксин для мутаций заявок
    """

    request_model = None
    request = None
    form = NamePhoneAndProjectForm
    send_to_amocrm = True

    ok = Boolean()
    errors = List(ErrorType)

    class Arguments:
        input = NameAndPhoneInput(required=True)

    @classmethod
    def mutate(cls, obj, info, input=None):
        form = cls.form(data=input)
        if form.is_valid():
            if settings.DEBUG:
                qs = cls.request_model.objects.filter(
                    phone=form.cleaned_data.get("phone"), date__gt=now() - timedelta(seconds=5)
                )
                if qs.exists():
                    return cls(ok=True, request=qs.first())

            instance = cls.request_model.objects.create(**cls.get_instance_data(form))
            RequestEmail(instance, info.context)()
            if cls.send_to_amocrm:
                instance.send_amocrm_lead(info.context)
            return cls(ok=True, request=instance)
        else:
            return cls(ok=False, request=None, errors=collect_form_errors(form))

    @classmethod
    def get_instance_data(cls, form) -> dict:

        data: dict = {"phone": form.cleaned_data.get("phone")}
        slug = form.cleaned_data.get("project_slug")
        project = Project.objects.get(slug=slug) if slug else None
        property_type = form.cleaned_data.get("property_type") or ""
        property_id = form.cleaned_data.get("property") or None
        related_object = form.cleaned_data.get("related_object") or None
        interval = form.cleaned_data.get("interval")
        name = form.cleaned_data.get("name", "")
        from_url = form.cleaned_data.get("from_url")
        if project:
            data.update({"project": project})
        if property_type:
            data.update({"property_type": property_type})
        if property_id:
            data.update({"property_id": property_id})
        if related_object:
            data.update({"related_object": related_object})
        if interval:
            data.update({"interval": interval})
        if name:
            data.update({"name": name})
        if from_url:
            data.update({"from_url": from_url})
        return data
