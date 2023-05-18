from django.conf import settings
from django.http import HttpRequest
from django.db.models import Model, Q
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .constants import RequestType
from .models import Manager


class RequestEmail:

    html_template = "request_forms/email.html"

    def __init__(self, instance: Model, http_request: HttpRequest):
        self.instance = instance
        self.http_request = http_request

    def __call__(self, *args, **kwargs):
        send_mail(
            subject=self.subject,
            message=self.subject,
            from_email=settings.SERVER_EMAIL,
            recipient_list=self.recipient_list,
            html_message=self.html_message,
        )

    @property
    def subject(self) -> str:
        if hasattr(self.instance, "form"):
            subject = str(self.instance.form)
        elif hasattr(self.instance, "email_subject"):
            subject = self.instance.email_subject
        else:
            subject = self.instance._meta.verbose_name
        return subject

    @property
    def recipient_list(self) -> list:

        q_filter = Q(is_active=True, type_list__contains=[self._get_request_type()])
        if hasattr(self.instance, "property_type") and self.instance.property_type:
            q_filter &= Q(property_type_list__contains=[self.instance.property_type])
        if not settings.TESTING:
            if hasattr(self.http_request, "site") and hasattr(self.http_request.site, "city"):
                q_filter &= Q(cities=self.http_request.site.city)

        manager_emails = list(Manager.objects.filter(q_filter).values_list("email", flat=True))
        return manager_emails

    @property
    def html_message(self):
        return render_to_string(self.html_template, context={"request": self.instance})

    def _get_request_type(self) -> str:
        for choice in RequestType.choices:
            if self.instance._meta.verbose_name in choice:
                return choice[0]
