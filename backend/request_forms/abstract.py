from django.db import models
from django.core.handlers.wsgi import WSGIRequest
from phonenumber_field.modelfields import PhoneNumberField

from amocrm.models import AmoCRMManager
from amocrm.services import AmoCRM
from amocrm.tasks import send_amocrm_lead
from app.settings import TESTING
from properties.constants import PropertyType
from common.utils import get_utm_data


class RequestBaseModel(models.Model):
    """
    Базовая модель заявки
    """

    name = models.CharField(verbose_name="Имя", max_length=200)
    phone = PhoneNumberField(verbose_name="Номер")
    date = models.DateTimeField(verbose_name="Дата и время отправки", auto_now_add=True)
    property_type = models.CharField(
        verbose_name="Тип", max_length=20, blank=True, choices=PropertyType.choices
    )

    project = models.ForeignKey(
        verbose_name="Проект",
        to="projects.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self._meta.verbose_name

    def send_amocrm_lead(self, request: WSGIRequest) -> None:
        if TESTING:
            return

        setattr(self, "http_request", request)

        pipeline_id, pipeline_status_id, resp_user_id = self.get_pipeline_ids()

        send_amocrm_lead.delay(
            self.name,
            str(self.phone),
            description=self.get_description(),
            pipeline_status_id=pipeline_status_id,
            pipeline_id=pipeline_id,
            resp_user_id=resp_user_id,
            name_lead="Заявка с сайта",
            text=self.format_text(),
            custom_fields=self.get_custom_fields(),
        )

    def get_description(self):
        return str(self.form) if hasattr(self, "form") else self._meta.verbose_name

    def get_current_site(self):
        if self.project:
            return self.project.city.site
        return self.http_request.site

    def format_text(self):
        format_text = f"Форма: {self.get_description()}\n"
        if hasattr(self, "http_request") and getattr(self, "http_request"):
            referer = self.http_request.headers.get("referer")
            if referer:
                format_text += f"Ссылка на страницу откуда пришла заявка:{referer}\n"
        if hasattr(self, "phone") and getattr(self, "phone"):
            format_text += f"Номер телефона контакта: {self.phone} \n"
        return format_text

    def get_pipeline_ids(self):
        default_manager = AmoCRMManager.objects.default()
        assert default_manager, "Default manager is not set!"

        current_site = self.get_current_site()
        if self._check_tmn_commercial(current_site):
            resp_user_id = current_site.city.amocrmmanager.comm_crm_id
            pipeline_id = current_site.city.amocrmmanager.comm_pipeline_id
            pipeline_status_id = current_site.city.amocrmmanager.comm_pipeline_status_id
        else:
            resp_user_id = default_manager.crm_id
            pipeline_id = default_manager.pipeline_id
            pipeline_status_id = default_manager.pipeline_status_id
        return pipeline_id, pipeline_status_id, resp_user_id

    def get_custom_fields(self) -> list:
        return AmoCRM.get_custom_fields(
            property_type=self.property_type,
            project_enum=self.project.amocrm_enum if self.project else None,
            project_name=self.project.amocrm_name if self.project else None,
            roistat_visit=self.http_request.COOKIES.get("roistat_visit"),
            smart_visitor_id=self.http_request.COOKIES.get("smart_visitor_id"),
            smart_session_id=self.http_request.COOKIES.get("smart_session_id"),
            utm_data=get_utm_data(self.http_request.COOKIES),
            metrika_cid=self.http_request.COOKIES.get("_ym_uid"),
            google_cid=(
                self.http_request.COOKIES.get("_ga")[6:]
                if self.http_request.COOKIES.get("_ga") is not None
                else ""
            ),
            city_name=self.project.city.short_name
            if self.project
            else self.http_request.site.city.short_name,
            url_address=self.http_request.headers.get("referer"),
        )

    def _check_tmn_commercial(self, current_site):
        return (
            current_site.city.short_name == "ТМН"
            and self.property_type == PropertyType.COMMERCIAL
            or self._meta.verbose_name == "Заявка на аренду коммерческого помещения"
        )
