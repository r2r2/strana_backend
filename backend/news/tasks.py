from celery import shared_task
from django.utils.timezone import now

from .models import News
from .constants import NewsType


@shared_task
def deactivate_old_actions_task():
    # деактивация акций, дата окончания которых меньше текущей
    actions = News.objects.filter(published=True, type=NewsType.ACTION, end__lt=now())
    actions.update(published=False)
