from django.db import models


class AssignClientTemplate(models.Model):
    """
    Модель СМС для закрепления клиента
    """
    text: str = models.TextField(verbose_name="Текст открепления")
    title: str = models.CharField(verbose_name="Название", max_length=255, null=True, blank=True)
    success_assign_text: str = models.TextField(
        verbose_name="Текст страницы успешного закрепления",
        blank=True,
        null=True,
    )
    success_unassign_text: str = models.TextField(
        verbose_name="Текст страницы успешного открепления",
        blank=True,
        null=True,
    )
    city: models.ForeignKey = models.ForeignKey(
        to='cities.Cities',
        related_name='assign_clients',
        on_delete=models.CASCADE,
        verbose_name='Город',
    )
    sms: models.ForeignKey = models.ForeignKey(
        to='notification_templates.SmsTemplate',
        related_name='assign_clients',
        on_delete=models.CASCADE,
        verbose_name='Шаблон СМС',
    )
    default: bool = models.BooleanField(verbose_name="По умолчанию", default=False)
    created_at = models.DateTimeField(verbose_name="Когда создано", help_text="Когда создано", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Когда обновлено", help_text="Когда обновлено", auto_now=True)

    def __str__(self) -> str:
        return f'{self.city.name} - {self.text}'

    class Meta:
        managed = False
        db_table = 'notifications_assignclient'
        verbose_name = 'СМС для закрепления клиента'
        verbose_name_plural = 'СМС для закрепления клиентов'
