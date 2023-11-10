from django.db import models


class EmailFooterTemplate(models.Model):
    """
    Шаблоны футеров писем.
    """

    text = models.TextField(
        verbose_name="Текст шаблона футера письма",
    )
    description = models.TextField(
        verbose_name="Описание назначения шаблона футера письма",
        help_text="Не участвует в бизнес-логике, поле для доп. описания",
        blank=True,
    )
    slug = models.CharField(
        max_length=100,
        verbose_name="Слаг шаблона футера письма",
        help_text="Максимум 100 символов, для привязки к шаблону на беке",
        unique=True,
    )
    is_active = models.BooleanField(
        verbose_name="Шаблон футера письма активен",
        default=True,
        help_text="Добавлять или нет шаблон футера письма",
    )
    created_at = models.DateTimeField(verbose_name="Когда создано", help_text="Когда создано", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Когда обновлено", help_text="Когда обновлено", auto_now=True)

    def __str__(self) -> str:
        return (
            f"{self.description} ({self.slug})"
            if self.slug and self.description
            else str(self.id)
        )

    class Meta:
        db_table = "notifications_email_footers"
        verbose_name = "Шаблон футера письма"
        verbose_name_plural = " 4.1.2. [Справочник] Шаблоны футера писем"
