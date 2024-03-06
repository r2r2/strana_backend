from django.db import models

from common.models import TimeBasedMixin


class FeedbackSettings(TimeBasedMixin, models.Model):
    """
    Настройки форм обратной связи
    """

    class Meta:
        managed = False
        db_table = 'settings_feedback'
        verbose_name = "Настройки форм обратной связи"
        verbose_name_plural = "15.5. Настройки форм обратной связи"
