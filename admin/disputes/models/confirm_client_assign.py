from django.db import models


class ConfirmClientAssign(models.Model):
    """
    Модель подтверждения закрепления клиента за агентом
    """
    agent = models.ForeignKey(
        to="users.CabinetUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Агент",
        related_name="agent_confirm_client_assign",
    )
    client = models.ForeignKey(
        to="users.CabinetUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Клиент",
        related_name="client_confirm_client_assign",
        db_index=True,
    )
    agency = models.ForeignKey(
        to="users.Agency",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Агентство",
    )
    assigned_at = models.DateTimeField(verbose_name="Дата и время закрепления", auto_now_add=True)
    assign_confirmed_at = models.DateTimeField(
        verbose_name="Дата и время подтверждения закрепления",
        null=True,
        blank=True
    )
    unassigned_at = models.DateTimeField(verbose_name="Дата и время отказа от агента", null=True, blank=True)
    comment = models.TextField(verbose_name="Комментарий агента при закреплении", null=True, blank=True)

    def __str__(self):
        return f"{self.client} закреплен за {self.agent}"

    class Meta:
        managed = False
        verbose_name = "Подтверждение закрепления клиента за агентом"
        verbose_name_plural = "6.4. [Исторические данные] Подтверждения закрепления клиента за агентом"
        db_table = "users_confirm_client_assign"
