# pylint: disable=no-member,invalid-str-returned
from django.db import models


class Dispute(models.Model):
    """
    Оспаривание статуса клиента
    """

    requested = models.DateTimeField(verbose_name="Запрошено", null=True, blank=True)
    dispute_requested = models.DateTimeField(
        verbose_name="Время оспаривания", null=True, blank=True
    )
    status_fixed: bool = models.BooleanField(
        verbose_name="Закрепить статус за клиентом", default=False
    )
    unique_status = models.ForeignKey(
        verbose_name="Статус уникальности",
        to="disputes.UniqueStatus",
        on_delete=models.CASCADE,
        related_name="user_check_checks",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        verbose_name="Пользователь",
        to="users.CabinetUser",
        on_delete=models.SET_NULL,
        related_name="users_checks",
        null=True,
        blank=True,
    )
    agent = models.ForeignKey(
        verbose_name="Агент",
        to="users.CabinetUser",
        on_delete=models.SET_NULL,
        related_name="agents_checks",
        null=True,
        blank=True,
    )
    dispute_agent = models.ForeignKey(
        verbose_name="Оспаривающий агент",
        to="users.CabinetUser",
        on_delete=models.SET_NULL,
        related_name="dispute_agents_checks",
        null=True,
        blank=True,
    )
    agency = models.ForeignKey(
        verbose_name="Агентство",
        to="users.Agency",
        on_delete=models.SET_NULL,
        related_name="agencies_checks",
        null=True,
        blank=True,
    )
    admin = models.ForeignKey(
        verbose_name="Админ",
        to="users.CabinetUser",
        on_delete=models.SET_NULL,
        related_name="admin_checks",
        null=True,
        blank=True,
    )
    comment = models.TextField(verbose_name="Комментарий агента", blank=True)
    admin_comment = models.TextField(verbose_name="Комментарий менеджера", blank=True)
    send_admin_email = models.BooleanField(
        default=False,
        verbose_name="Отправлено письмо администраторам",
    )
    send_rop_email: bool = models.BooleanField(
        default=False, verbose_name="Отправлено письмо РОПу"
    )
    amocrm_id = models.IntegerField(
        verbose_name="ID сделки в amoCRM, по которой была проверка",
        null=True,
        blank=True,
    )
    term_uid = models.CharField(
        verbose_name="UID условия проверки на уникальность",
        max_length=255,
        blank=True,
    )
    term_comment = models.TextField(
        verbose_name="Комментарий к условию проверки на уникальность",
        blank=True,
    )
    button_slug = models.CharField(
        verbose_name="Слаг кнопки",
        max_length=255,
        blank=True,
    )
    button_pressed = models.BooleanField(
        verbose_name="Кнопка была нажата", default=False
    )
    dispute_status = models.ForeignKey(
        verbose_name="Статус оспаривания",
        to="disputes.DisputeStatus",
        on_delete=models.SET_NULL,
        related_name="dispute_statu",
        null=True,
    )

    def __str__(self) -> str:
        return str(self.id)

    # TODO full_name нужно нормально сделать в модели User (на будущее)
    @property
    def client_full_name(self):
        return (
            self.user.full_name() if self.user and self.user.full_name() else self.user
        )

    @property
    def agent_full_name(self):
        return (
            self.agent.full_name()
            if self.agent and self.agent.full_name()
            else self.agent
        )

    @property
    def dispute_agent_full_name(self):
        return (
            self.agent.full_name()
            if self.agent and self.agent.full_name()
            else self.agent
        )

    @property
    def admin_full_name(self):
        return (
            self.admin.full_name()
            if self.admin and self.admin.full_name()
            else self.admin
        )

    class Meta:
        managed = False
        db_table = "users_checks"
        verbose_name = "Статус клиента"
        verbose_name_plural = "6.5. [Справочник] Текущие статусы проверки клиентов"
        ordering = ["requested"]
