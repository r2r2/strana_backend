from booking.models import Booking
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Пользователь
    """

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")


class CabinetUserQuerySet(models.QuerySet):
    def annotate_file_data(self):
        return self.annotate(
            booking_count=models.Count("booking"),
            booking_active_count=models.Count(
                "booking",
                filter=models.Q(booking__active=True)),
            booking_lk_count=models.Count(
                "booking",
                filter=models.Q(booking__created_source=Booking.CreatedSourceChoices.LK)),
            booking_lk_active=models.Count(
                "booking",
                filter=models.Q(booking__created_source=Booking.CreatedSourceChoices.LK) &
                models.Q(booking__active=True)),
        )


class CabinetUser(models.Model):
    """
    Пользователь ЛК
    """
    username = models.CharField(unique=True, max_length=100, blank=True, null=True)
    password = models.CharField(max_length=200, blank=True, null=True)
    email = models.CharField(unique=True, max_length=100, blank=True, null=True)
    phone = models.CharField(unique=True, max_length=20, blank=True, null=True)
    code = models.CharField(max_length=4, blank=True, null=True)
    code_time = models.DateTimeField(blank=True, null=True)
    token = models.UUIDField(blank=True, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    surname = models.CharField(max_length=50, blank=True, null=True)
    patronymic = models.CharField(max_length=50, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField()
    is_superuser = models.BooleanField()
    is_deleted = models.BooleanField()
    amocrm_id = models.BigIntegerField(blank=True, null=True)
    type = models.CharField(max_length=20)
    role = models.ForeignKey(
        "users.UserRole",
        models.SET_NULL,
        related_name="users",
        null=True,
        blank=True,
        verbose_name="Роль",
        help_text="Роль пользователя"
    )
    is_imported = models.BooleanField()
    email_token = models.CharField(max_length=100, blank=True, null=True)
    passport_series = models.CharField(max_length=20, blank=True, null=True)
    passport_number = models.CharField(max_length=20, blank=True, null=True)
    is_onboarded = models.BooleanField()
    agency = models.ForeignKey("agencies.Agency", models.DO_NOTHING, blank=True, null=True)
    duty_type = models.CharField(max_length=20, blank=True, null=True)
    is_approved = models.BooleanField()
    one_time_password = models.CharField(max_length=200, blank=True, null=True)
    discard_token = models.CharField(max_length=100, blank=True, null=True)
    work_end = models.DateField(blank=True, null=True)
    reset_time = models.DateTimeField(blank=True, null=True)
    maintained_id = models.IntegerField(unique=True, blank=True, null=True)
    agent = models.ForeignKey("self", models.DO_NOTHING, blank=True, null=True)
    work_start = models.DateField(blank=True, null=True)
    interested_project = models.ForeignKey(
        "projects.Project", models.DO_NOTHING, blank=True, null=True
    )
    interested_type = models.CharField(max_length=20, blank=True, null=True)
    is_brokers_client = models.BooleanField()
    is_independent_client = models.BooleanField()
    is_test_user = models.BooleanField(help_text="Сделки с тестовым клиентом будут отмечаться тегом 'Тест' в АМО")
    receive_admin_emails = models.BooleanField(
        verbose_name="Получать письма администратора",
        help_text="При отмеченном флаге, если пользователь имеет роль 'Администратор', он будет получать письма администратора на указанный Email"
    )
    sms_send = models.BooleanField(verbose_name="СМС отправлено", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    auth_first_at = models.DateTimeField(verbose_name="Дата первой авторизации", blank=True, null=True)
    interested_sub = models.BooleanField(verbose_name="Подписка на избранное", default=False)
    assignation_comment = models.TextField(verbose_name="Комментарий при закреплении клиента", null=True, blank=True)
    objects = CabinetUserQuerySet.as_manager()

    def __str__(self) -> str:
        surname_n = f"{self.surname} {self.name[0]}." \
            if self.surname and self.name else None
        patronymic = f"{self.patronymic[0]}." if self.patronymic else None
        user_info_list: list[str] = [self.phone, surname_n, patronymic]
        info = map(lambda user_info: str(user_info) if user_info else "", user_info_list)
        return " ".join(info)

    def full_name(self):
        return f'{self.name or ""} {self.surname or ""} {self.patronymic or ""}'.strip()

    class Meta:
        managed = False
        db_table = "users_user"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-created_at"]
