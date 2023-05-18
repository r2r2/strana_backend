from celery import shared_task
from django.utils import timezone
@shared_task
def send_amo_lead_callback_request():
    from .models import CallbackRequest
    for instance in CallbackRequest.objects.filter(amo_send=False):
        if not instance.in_interval:
            continue
        instance.send_amocrm_lead_without_http()
