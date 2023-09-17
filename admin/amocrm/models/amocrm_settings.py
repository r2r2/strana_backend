from django.db import models
from solo.models import SingletonModel


class AmoCRMSettings(SingletonModel):
    """
    Настройки AmoCRM
    """

    client_id = models.TextField(verbose_name="ID интеграции", blank=False)
    client_secret = models.TextField(verbose_name="Секретный ключ", blank=False)
    access_token = models.TextField(verbose_name="Access token", blank=False)
    refresh_token = models.TextField(verbose_name="Refresh token", blank=False)
    redirect_uri = models.CharField(max_length=255, verbose_name="URI редиректа", blank=False)

    def __str__(self) -> str:
        return "Настройки AmoCRM"

    def is_valid(self) -> bool:
        return bool(
            self.client_id
            and self.client_secret
            and self.access_token
            and self.refresh_token
            and self.redirect_uri
        )

    class Meta:
        verbose_name = "Настройки AmoCRM"
        db_table = "amocrm_amocrm_settings"
