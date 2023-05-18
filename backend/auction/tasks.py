from celery import shared_task
from django.apps import apps
from .models import Notification


def send_single_notification(pk: int):
    Notification = apps.get_model("auction", "Notification")
    notification = Notification.objects.get(pk=pk)
    notification.notify_customer()


@shared_task
def notify_start_auction_task():
    notifications = Notification.objects.filter(is_sent=False).timeframed()
    for n in notifications:
        send_single_notification(n.pk)

    notifications.update(is_sent=True)
