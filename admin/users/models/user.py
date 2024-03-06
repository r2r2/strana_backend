from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from booking.models import Booking


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
            booking_count=models.Count("booking_user"),
            booking_active_count=models.Count(
                "booking_user",
                filter=models.Q(booking_user__active=True)),
            booking_lk_count=models.Count(
                "booking_user",
                filter=models.Q(booking_user__booking_source__slug=Booking.CreatedSourceChoices.LK)),
            booking_lk_active=models.Count(
                "booking_user",
                filter=models.Q(booking_user__booking_source__slug=Booking.CreatedSourceChoices.LK) &
                models.Q(booking_user__active=True)),
        )


class CabinetUser(models.Model):
    """
    Пользователь ЛК
    """
    class OriginType(models.TextChoices):
        AMOCRM = "amocrm", _("Импорт из АМО CRM")
        SMS = "sms", _("Авторизация через СМС")
        AGENT_ASSIGN = "agent_assign", _("Закрепление агентом")

    class UserType(models.TextChoices):
        """
        Тип пользователя
        """
        ADMIN: str = "admin", _("Админ")
        AGENT: str = "agent", _("Агент")
        CLIENT: str = "client", _("Клиент")
        REPRES: str = "repres", _("Представитель")
        MANAGER: str = "manager", _("Менеджер")
        ROP: str = "rop", _("Руководитель отдела продаж")

    email = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True, help_text="Должен быть в формате “'+7XXXXXXXXXX")
    username = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="В шифрованном виде. Используется только для авторизации агентов/агентств/администраторов "
                  "(клиенты авторизуются по коду)",
    )
    code = models.CharField(
        max_length=4, blank=True, null=True, help_text="Отправленный при авторизации клиента SMS-код"
    )
    code_time = models.DateTimeField(blank=True, null=True, help_text="Количество времени, пока SMS код активен")
    token = models.UUIDField(
        blank=True, null=True, help_text="Токен для валидации кода SMS. Генерируется при запросе кода"
    )
    name = models.CharField(max_length=50, blank=True, null=True)
    surname = models.CharField(max_length=50, blank=True, null=True)
    patronymic = models.CharField(max_length=50, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField()
    is_deleted = models.BooleanField(help_text="Удаленные пользователи не могут войти на сайт")
    amocrm_id = models.BigIntegerField(blank=True, null=True)
    type = models.CharField(
        choices=UserType.choices,
        max_length=20,
        verbose_name="Тип/Роль",
        help_text="Роль пользователя в системе",
        db_index=True,
    )
    origin = models.CharField(
        choices=OriginType.choices,
        max_length=30,
        default=None,
        null=True,
        verbose_name="Источник",
    )
    role = models.ForeignKey(
        "users.UserRole",
        models.SET_NULL,
        related_name="users",
        null=True,
        blank=True,
        verbose_name="Роль",
        help_text="Роль пользователя",
        db_index=True,
    )
    is_imported = models.BooleanField(
        help_text="Проверяет при валидации (при первой проверке телефона [регистрации клиента] - FALSE, "
                  "после валидации - ставится TRUE и создается в АМО)",
    )
    email_token = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Токен эл. почты пользователя, который позволяет авторизоваться/активировать почту в ЛК "
                  "через ссылку в письме (не используется)",
    )
    passport_series = models.CharField(max_length=20, blank=True, null=True)
    passport_number = models.CharField(max_length=20, blank=True, null=True)
    is_onboarded = models.BooleanField()
    agency = models.ForeignKey(
        "users.Agency",
        models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Агентство",
        help_text="Для клиента агентство, за которым он закреплен; для агента - агентство, в котором он работает",
    )
    maintained = models.OneToOneField(
        "users.Agency",
        models.SET_NULL,
        verbose_name="Главный агентства",
        related_name="maintainer",
        blank=True,
        null=True,
    )
    is_approved = models.BooleanField(
        help_text="Подтвержден пользователь (при авторизации) или нет, не подтвержденные пользователи не имеют "
                  "право войти в ЛК (по умолчанию подтверждены все)",
    )
    one_time_password = models.CharField(max_length=200, blank=True, null=True)
    discard_token = models.CharField(max_length=100, blank=True, null=True)
    work_end = models.DateField(blank=True, null=True)
    reset_time = models.DateTimeField(blank=True, null=True)
    agent = models.ForeignKey(
        "self",
        models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Агент",
        help_text="[Для клиентов] Агент, закрепленный за клиентом",
    )
    work_start = models.DateField(blank=True, null=True, help_text="Дата начала работы с клиентом (закрепления)")
    interested_project = models.ForeignKey(
        "properties.Project",
        models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Интересующий проект",
        help_text="Фиксирует, какой проект заинтересовал пользователя при закрепления",
    )
    interested_type = models.CharField(
        max_length=20, blank=True, null=True, help_text="Интересующий тип недвижимости (не используется)"
    )
    is_brokers_client = models.BooleanField(
        help_text="Флагом отмечены клиенты агентств (т.е. они связаны с каким-то агентом)",
    )
    is_independent_client = models.BooleanField(
        help_text="Флагом отмечены клиенты пришедшие самостоятельно и работающие напрямую "
                  "с застройщиком (т.е. они не связаны с каким-то агентом)",
    )
    is_test_user = models.BooleanField(help_text="Сделки с тестовым клиентом будут отмечаться тегом 'Тест' в АМО")
    sms_send = models.BooleanField(verbose_name="СМС отправлено", default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    auth_first_at = models.DateTimeField(verbose_name="Дата первой авторизации", blank=True, null=True)
    auth_last_at = models.DateTimeField(verbose_name="Дата последней авторизации", blank=True, null=True)
    interested_sub = models.BooleanField(verbose_name="Подписка на избранное", default=False)
    assignation_comment = models.TextField(
        verbose_name="Комментарий при закреплении клиента",
        null=True,
        blank=True,
        help_text="Комментарий агента, указанный при закреплении данного клиента",
    )
    user_cities = models.ManyToManyField(
        to="references.Cities",
        through="CityUserThrough",
        through_fields=(
            "user",
            "city",
        ),
        verbose_name="Город пользователей",
        blank=True,
        related_name="user_cities",
        help_text="Город связанного с пользователем агентства",
    )

    loyalty_point_amount = models.IntegerField(
        verbose_name="Остаток баллов по программе лояльности",
        help_text="Только для информации, редактируется через микросервис лояльности (только агенты и представители)",
        null=True,
        blank=True,
    )
    loyalty_status_name = models.CharField(
        verbose_name="Статус лояльности",
        max_length=100,
        help_text="Только для информации, редактируется через микросервис лояльности (только агенты и представители)",
        null=True,
        blank=True,
    )
    loyalty_status_icon = models.FileField(
        verbose_name="Изображение статуса лояльности",
        max_length=300,
        upload_to="u/a/f",
        null=True,
        blank=True,
    )
    loyalty_status_level_icon = models.FileField(
        verbose_name="Цветное изображение статуса лояльности",
        max_length=300,
        upload_to="u/a/f",
        null=True,
        blank=True,
    )
    loyalty_status_substrate_card = models.FileField(
        verbose_name="Подложка (карточка участника) статуса лояльности",
        max_length=300,
        upload_to="u/a/f",
        null=True,
        blank=True,
    )
    loyalty_status_icon_profile = models.FileField(
        verbose_name="Подложка (профиль) статуса лояльности",
        max_length=300,
        upload_to="u/a/f",
        null=True,
        blank=True,
    )
    date_assignment_loyalty_status = models.DateTimeField(
        verbose_name="Дата присвоения статуса лояльности",
        blank=True,
        null=True,
    )
    is_offer_accepted = models.BooleanField(
        verbose_name="Принята оферта",
        default=False,
    )
    ready_for_super_auth = models.BooleanField(
        verbose_name="Под данным пользователем может авторизоваться суперюзер",
        default=False,
    )
    can_login_as_another_user = models.BooleanField(
        verbose_name="Суперпользователь",
        default=False,
        help_text="Нельзя менять хэш пароль у суперюзеров",
    )
    client_token_for_superuser = models.CharField(
        verbose_name="Токен авторизации для клиента (для использования суперпользователями)",
        max_length=300,
        null=True,
        blank=True,
    )

    objects = CabinetUserQuerySet.as_manager()

    def __str__(self) -> str:
        surname_n = f"{self.surname} {self.name[0]}." \
            if self.surname and self.name else None
        patronymic = f"{self.patronymic[0]}." if self.patronymic else None
        user_info_list: list[str] = [self.phone, surname_n, patronymic]
        info = map(lambda user_info: str(user_info) if user_info else "", user_info_list)
        return " ".join(info) + f" (AMOCRMID {self.amocrm_id})"

    def full_name(self):
        return f'{self.name or ""} {self.surname or ""} {self.patronymic or ""}'.strip()

    class Meta:
        managed = False
        db_table = "users_user"
        verbose_name = "Пользователь"
        verbose_name_plural = " 2.1. [Пользователи] Все"
        ordering = ["-created_at"]
        unique_together = [["role", "phone"], ["role", "email"], ["role", "username"], ["role", "amocrm_id"]]


class CabinetClient(CabinetUser):
    """
    Прокси модель Клиентов
    """
    class Meta:
        proxy = True
        verbose_name = "Клиент"
        verbose_name_plural = " 2.8. [Пользователи] Клиенты"


class CabinetAgent(CabinetUser):
    """
    Прокси модель Агентов
    """
    class Meta:
        proxy = True
        verbose_name = "Агент"
        verbose_name_plural = " 2.9. [Пользователи] Агенты"


class CabinetAdmin(CabinetUser):
    """
    Прокси модель Администраторов
    """
    class Meta:
        proxy = True
        verbose_name = "Администраторы"
        verbose_name_plural = "2.10. [Пользователи] Администраторы"
