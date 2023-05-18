from django.db import models

from common import TimeBasedMixin


class BaseQuestionnaireModel(TimeBasedMixin, models.Model):
    """
    Базовая модель опросника
    """

    class Meta:
        abstract = True
