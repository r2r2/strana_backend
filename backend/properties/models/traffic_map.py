from django.db import models

from common.fields import PolygonField

from ..constants import PropertyType
from ..querysets import PropertyQuerySet


class TrafficMap(models.Model):
    """
    Трафик на карте
    """

    objects = PropertyQuerySet.as_manager()
    project = models.ForeignKey(
        verbose_name="Проект", to="projects.Project", on_delete=models.CASCADE
    )
    name = models.CharField("Название", unique=True, db_index=True, max_length=32)

    map_hover = models.TextField(verbose_name="Обводка на карте", blank=True)

    weekday_morning = models.DecimalField(
        verbose_name="Будни утро", max_digits=8, decimal_places=2, null=True, blank=True
    )
    weekday_day = models.DecimalField(
        verbose_name="Будни день", max_digits=8, decimal_places=2, null=True, blank=True
    )
    weekday_evening = models.DecimalField(
        verbose_name="Будни вечер", max_digits=8, decimal_places=2, null=True, blank=True
    )

    weekday_current = models.DecimalField(
        verbose_name="Будни текущий трафик", max_digits=8, decimal_places=2, null=True, blank=True
    )

    weekend_morning = models.DecimalField(
        verbose_name="Выходные утро", max_digits=8, decimal_places=2, null=True, blank=True
    )
    weekend_day = models.DecimalField(
        verbose_name="Выходные день", max_digits=8, decimal_places=2, null=True, blank=True
    )
    weekend_evening = models.DecimalField(
        verbose_name="Выходные вечер", max_digits=8, decimal_places=2, null=True, blank=True
    )

    weekend_current = models.DecimalField(
        verbose_name="Выходные текущий трафик", max_digits=8, decimal_places=2, null=True, blank=True
    )

    class Meta:
        verbose_name = "Трафик на карте"
        verbose_name_plural = "Трафик на карте"
