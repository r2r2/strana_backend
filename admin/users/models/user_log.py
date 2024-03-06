from common.loggers.models import AbstractLog
from django.db import models


class UserLog(AbstractLog):
    user = models.ForeignKey(
        "users.CabinetUser",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Пользователь',
        db_index=True,
    )

    class Meta:
        managed = False
        db_table = "users_userlog"
        verbose_name = "Лог пользователя"
        verbose_name_plural = "Логи пользователей"
