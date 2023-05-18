from common.loggers.models import AbstractLog
from django.db import models


class AgencyLog(AbstractLog):
    agency = models.ForeignKey(
        "agencies.Agency", models.CASCADE, blank=True, null=True, verbose_name='Агентство'
    )


    class Meta:
        managed = False
        db_table = "agencies_agencylog"
        verbose_name = "Лог агентства"
        verbose_name_plural = "Логи агентств"
