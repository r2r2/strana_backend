from django.db import models


class EmailHeaderTemplate(models.Model):
    """
    Шаблоны хэдеров писем.
    """

    text = models.TextField(
        verbose_name="Текст шаблона хэдера письма",
    )
    description = models.TextField(
        verbose_name="Описание назначения шаблона хэдера письма",
        help_text="Не участвует в бизнес-логике, поле для доп. описания",
        blank=True,
    )
    slug = models.CharField(
        max_length=100,
        verbose_name="Слаг шаблона хэдера письма",
        help_text="Максимум 100 символов, для привязки к шаблону на беке",
        unique=True,
    )
    is_active = models.BooleanField(
        verbose_name="Шаблон хэдера письма активен",
        default=True,
        help_text="Добавлять или нет шаблон хэдера письма",
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
        db_table = "notifications_email_headers"
        verbose_name = "Шаблон хэдера письма"
        verbose_name_plural = " 4.1.1. [Справочник] Шаблоны хэдеров писем"
