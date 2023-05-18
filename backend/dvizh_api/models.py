from solo.models import SingletonModel

from django.db import models


class DvizhApiSettings(SingletonModel):
    endpoint = models.URLField(verbose_name="URL API", default="https://gql.make.dvizh.io/gql")
    user = models.EmailField(verbose_name="Email Пользователя")
    password = models.CharField(verbose_name="Пароль", max_length=32)
    token = models.TextField(verbose_name="Токен авторизации", null=True, editable=False)

    class Meta:
        verbose_name = verbose_name_plural = "Настройки для API Движ."
