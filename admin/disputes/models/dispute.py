# pylint: disable=no-member,invalid-str-returned
from typing import Optional

from django.db import models


class Dispute(models.Model):
    """
    Оспаривание статуса клиента
    """

    user = models.ForeignKey(
        "users.CabinetUser",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='client',
        verbose_name='Клиент',
        help_text='Проверяемый клиент',
    )
    agent = models.ForeignKey(
        "users.CabinetUser",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='client_agent',
        verbose_name='Текущий агент',
        help_text='Агент, который в настоящее время закреплен за клиентом',
    )
    agency = models.ForeignKey(
        "users.Agency",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='agency',
        verbose_name='Текущее агентство клиента',
        help_text='Агентство, которое в настоящее время закреплено за клиентом',
    )
    dispute_agent = models.ForeignKey(
        "users.CabinetUser",
        models.DO_NOTHING,
        verbose_name='Оспаривающий агент',
        blank=True,
        null=True,
        related_name='dispute_agent',
        help_text='Агент, оспаривающий статус клиента',
    )
    admin = models.ForeignKey(
        "users.CabinetUser",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='admin',
        verbose_name='Обновлено администратором'
    )
    requested = models.DateTimeField(blank=True, null=True, verbose_name='Запрошено')
    dispute_requested = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Время оспаривания',
    )
    status_fixed = models.BooleanField(
        verbose_name="Закрепить статус за клиентом",
        help_text='При отметке этого чекбокса агент будет считаться “Уникальным” до момента следующего закрепления '
                  '(чтобы агент мог самостоятельно его закрепить)',
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий агента',
        help_text='Причина, по которой оспаривающий агент считает клиента своим',
    )
    admin_comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий менеджера',
        help_text="Внутренний комментарий (не отправляется агенту/клиенту)"
    )
    unique_status: models.ForeignKey = models.ForeignKey(
        to="disputes.UniqueStatus",
        verbose_name="Статус уникальности",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="checks",
    )
    send_admin_email: bool = models.BooleanField(default=False, verbose_name="Отправлено письмо администратору")
    amocrm_id: Optional[int] = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="ID сделки в amoCRM",
    )
    term_uid = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='UID условия проверки на уникальность',
    )
    term_comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий к условию проверки на уникальность',
    )

    def __str__(self) -> str:
        return str(self.id)

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
        verbose_name_plural = "6.5. [Справочник] Текущие статусы проверки клиентов"
        ordering = ["requested"]
