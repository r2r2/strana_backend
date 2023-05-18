from django.db import models

from common import TimeBasedMixin


class BaseTaskManagementModel(TimeBasedMixin, models.Model):
    """
    Базовая модель управления задачами
    """

    class Meta:
        abstract = True
