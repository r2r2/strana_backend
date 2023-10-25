from django.db import models


class EmailTemplateLkType(models.TextChoices):
    BROKER: str = "lk_broker", "ЛК Брокера"
    CLIENT: str = "lk_client", "ЛК Клиента"


class EmailTemplate(models.Model):
    """
    Шаблоны писем.
    """

    template_topic = models.TextField(
        verbose_name="Заголовок шаблона письма",
    )
    template_text = models.TextField(
        verbose_name="Текст шаблона письма",
        help_text="Могут быть использованы макросы (автоматически заменяемые при отправке регулярные выражения). "
                  "Уточняйте список макросов у разработчика для конкретного шаблона",
    )
    lk_type: str = models.CharField(
        verbose_name="Сервис ЛК, в котором применяется шаблон",
        choices=EmailTemplateLkType.choices,
        max_length=10,
        help_text="Не участвует в бизнес-логике, поле для фильтрации в админке",
    )
    mail_event = models.TextField(
        verbose_name="Описание назначения события отправки письма",
        null=True,
        blank=True,
        help_text="Не участвует в бизнес-логике, поле для доп. описания",
    )
    mail_event_slug = models.CharField(
        max_length=100,
        verbose_name="Слаг назначения события отправки письма",
        help_text="Максимум 100 символов, для привязки к событию на беке",
        unique=True,
    )
    header_template: models.ForeignKey = models.ForeignKey(
        to='notifications.EmailHeaderTemplate',
        on_delete=models.CASCADE,
        related_name='email_templates',
        verbose_name='Шаблон хэдера',
        help_text="Для вставки хэдера в шаблон должны быть добавлены теги <head></head>",
        null=True,
        blank=True,
    )
    footer_template: models.ForeignKey = models.ForeignKey(
        to='notifications.EmailFooterTemplate',
        on_delete=models.CASCADE,
        related_name='email_templates',
        verbose_name='Шаблон футера',
        help_text="Для вставки футера в шаблон должны быть добавлены теги <footer></footer>",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(
        verbose_name="Шаблон активен",
        default=True,
        help_text="Отправлять или нет сообщение из шаблона",
    )
    created_at = models.DateTimeField(verbose_name="Когда создано", help_text="Когда создано", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Когда обновлено", help_text="Когда обновлено", auto_now=True)

    def __str__(self) -> str:
        return self.mail_event_slug

    class Meta:
        db_table = "notifications_email_notification"
        verbose_name = "Шаблон письма"
        verbose_name_plural = "4.1. [Справочник] Шаблоны писем"
