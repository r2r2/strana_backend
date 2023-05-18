from django.db import models


class BrokerRegistration(models.Model):
    """
    Регистрация брокера
    """

    new_pwd_image = models.ImageField(max_length=500, blank=True, null=True, upload_to="p/br/i")
    login_pwd_image = models.ImageField(max_length=500, blank=True, null=True, upload_to="p/br/i")
    forgot_pwd_image = models.ImageField(max_length=500, blank=True, null=True, upload_to="p/br/i")
    forgot_send_image = models.ImageField(max_length=500, blank=True, null=True, upload_to="p/br/i")
    login_email_image = models.ImageField(max_length=500, blank=True, null=True, upload_to="p/br/i")
    enter_agency_image = models.ImageField(
        max_length=500, blank=True, null=True, upload_to="p/br/i"
    )
    confirm_send_image = models.ImageField(
        max_length=500, blank=True, null=True, upload_to="p/br/i"
    )
    enter_personal_image = models.ImageField(
        max_length=500, blank=True, null=True, upload_to="p/br/i"
    )
    enter_password_image = models.ImageField(
        max_length=500, blank=True, null=True, upload_to="p/br/i"
    )
    accept_contract_image = models.ImageField(
        max_length=500, blank=True, null=True, upload_to="p/br/i"
    )
    confirmed_email_image = models.ImageField(
        max_length=500, blank=True, null=True, upload_to="p/br/i"
    )

    def __str__(self) -> str:
        return self._meta.verbose_name

    class Meta:
        managed = False
        db_table = "pages_broker_registration"
        verbose_name = "Регистрация брокера"
        verbose_name_plural = "Регистрация брокера"


class CheckUnique(models.Model):
    """
    Проверка на уникальность
    """

    check_image = models.ImageField(max_length=500, blank=True, null=True, upload_to="p/cu/i")
    result_image = models.ImageField(max_length=500, blank=True, null=True, upload_to="p/cu/i")

    def __str__(self) -> str:
        return self._meta.verbose_name

    class Meta:
        managed = False
        db_table = "pages_check_unique"
        verbose_name = "Проверка на уникальность"
        verbose_name_plural = "Проверка на уникальность"


class ShowtimeRegistration(models.Model):
    """
    Запись на показ
    """

    result_image = models.ImageField(max_length=500, blank=True, null=True, upload_to="p/sr/i")

    def __str__(self) -> str:
        return self._meta.verbose_name

    class Meta:
        managed = False
        db_table = "pages_showtime_registration"
        verbose_name = "Запись на показ"
        verbose_name_plural = "Запись на показ"
