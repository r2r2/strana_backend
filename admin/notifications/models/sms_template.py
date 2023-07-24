from django.db import models


class SmsTemplateLkType(models.TextChoices):
    BROKER: str = "lk_broker", "ЛК Брокера"
    CLIENT: str = "lk_client", "ЛК Клиента"


class SmsTemplate(models.Model):
    """
    Шаблоны смс сообщений.
    """

    template_text = models.TextField(
        verbose_name="Текст шаблона смс сообщения",
        help_text="Могут быть использованы макросы (автоматически заменяемые при отправке регулярные выражения). "
                  "Уточняйте список макросов у разработчика для конкретного шаблона",
    )
    lk_type: str = models.CharField(
        verbose_name="Сервис ЛК, в котором применяется шаблон",
        choices=SmsTemplateLkType.choices,
        max_length=10,
        null=False,
        help_text="Не участвует в бизнес-логике, поле для фильтрации в админке",
    )
    sms_event = models.TextField(
        verbose_name="Описание назначения события отправки смс",
        null=True,
        blank=True,
        help_text="Не участвует в бизнес-логике, поле для доп. описания",
    )
    sms_event_slug = models.CharField(
        max_length=100,
        verbose_name="Слаг события отправки смс",
        help_text="Максимум 100 символов, для привязки к событию на беке",
        unique=True,
    )
    is_active = models.BooleanField(
        verbose_name="Шаблон активен",
        default=True,
        help_text="Отправлять или нет сообщение из шаблона",
    )
    created_at = models.DateTimeField(verbose_name="Когда создано", help_text="Когда создано", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Когда обновлено", help_text="Когда обновлено", auto_now=True)

    def __str__(self) -> str:
        return self.sms_event_slug

    class Meta:
        db_table = "notifications_sms_notification"
        verbose_name = "Шаблон смс сообщения"
        verbose_name_plural = "4.2. [Справочник] Шаблоны смс сообщений"
