from common.loggers.models import AbstractLog
from django.db import models


class UserLog(AbstractLog):
    user = models.ForeignKey(
        "users.CabinetUser", models.CASCADE, blank=True, null=True, verbose_name='Пользователь'
    )

    class Meta:
        managed = False
        db_table = "users_userlog"
        verbose_name = "Лог пользователя"
        verbose_name_plural = "Логи пользователей"
