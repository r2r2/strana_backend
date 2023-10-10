from django.db import models


class AddServiceSettings(models.Model):
    """
    Настройки доп. услуг
    """

    email: str = models.CharField(
        verbose_name="Email",
        max_length=100,
        null=True,
        help_text="Укажите почту, на которую будут отправляться заявки по доп. услугам",
    )

    def __str__(self) -> str:
        return self.email

    class Meta:
        managed = False
        db_table = "settings_add_service_settings"
        verbose_name = "почтовый адрес для рассылки"
        verbose_name_plural = "15.2. Настройки доп. услуг"
