from uuid import uuid4

from django.db import models


class Statistic(models.Model):
    """Статистика"""

    id = models.UUIDField("ID", primary_key=True, default=uuid4)

    metting = models.ForeignKey("panel_manager.Meeting", models.CASCADE, verbose_name="Встреча")
    slide = models.TextField("Слайд", blank=True)

    view = models.PositiveIntegerField("Количество показов", default=0)
    time = models.TimeField("Время показа", blank=True, null=True)

    class Meta:
        verbose_name = "Статистика"
        verbose_name_plural = "Статистика"

    def __str__(self):
        return f"{self.metting}: {self.slide} = {self.view} | {self.time}"
