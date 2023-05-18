# pylint: disable=no-member,invalid-str-returned
from django.db import models
from django.utils.translation import gettext_lazy as _


class Dispute(models.Model):
    """
    Оспаривание статуса клиента
    """

    # TODO : предлагаю вынести UserStatus из кабинета constants.py
    class UserStatus(models.TextChoices):
        """
        Статус пользователя
        """
        CHECK: str = "check", _("На проверке")
        UNIQUE: str = "unique", _("Уникальный")
        REFUSED: str = "refused", _("Отказался")
        NOT_UNIQUE: str = "not_unique", _("Не уникальный")
        DISPUTE: str = 'dispute', _("Оспаривание статуса")
        CAN_DISPUTE = "can_dispute", _("Закреплен, но можно оспорить")
        ERROR: str = 'error', _("Ошибка")

    user = models.ForeignKey(
        "users.CabinetUser", models.DO_NOTHING, blank=True, null=True, related_name='client', verbose_name='Клиент'
    )
    agent = models.ForeignKey(
        "users.CabinetUser",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='client_agent',
        verbose_name='Текущий агент'
    )
    agency = models.ForeignKey(
        "agencies.Agency",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='agency',
        verbose_name='Текущее агентство клиента'
    )
    dispute_agent = models.ForeignKey(
        "users.CabinetUser",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='dispute_agent',
        verbose_name='Оспаривающий агент'
    )
    admin = models.ForeignKey(
        "users.CabinetUser",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='admin',
        verbose_name='Обновлено администратором'
    )
    status = models.CharField(choices=UserStatus.choices, max_length=50, verbose_name='Статус')
    requested = models.DateTimeField(blank=True, null=True, verbose_name='Запрошено')
    dispute_requested = models.DateTimeField(blank=True, null=True, verbose_name='Время оспаривания')
    status_fixed = models.BooleanField(verbose_name="Закрепить статус за клиентом")
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий агента')
    admin_comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий менеджера',
        help_text="Внутренний комментарий (не отправляется агенту/клиенту)"
    )


    def __str__(self) -> str:
        return self.status if self.status else str(self.id)

    # TODO full_name нужно нормально сделать в модели User (на будущее)
    @property
    def client_full_name(self):
        return self.user.full_name() if self.user and self.user.full_name() else self.user

    @property
    def agent_full_name(self):
        return self.agent.full_name() if self.agent and self.agent.full_name() else self.agent

    @property
    def dispute_agent_full_name(self):
        return self.agent.full_name() if self.agent and self.agent.full_name() else self.agent

    @property
    def admin_full_name(self):
        return self.admin.full_name() if self.admin and self.admin.full_name() else self.admin

    class Meta:
        managed = False
        db_table = "users_checks"
        verbose_name = "Статус клиента"
        verbose_name_plural = "Статусы клиентов"
        ordering = ["status", "requested"]
