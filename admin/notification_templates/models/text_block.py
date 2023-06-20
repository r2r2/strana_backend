from django.db import models
from ckeditor.fields import RichTextField


class LkType(models.TextChoices):
    BROKER: str = "lk_broker", "ЛК Брокера"
    CLIENT: str = "lk_client", "ЛК Клиента"


class TextBlock(models.Model):
    """
    Текстовые блоки.
    """

    title = models.TextField(
        verbose_name="Заголовок блока",
        null=True,
        blank=True,
    )
    text = RichTextField(
        verbose_name="Текст блока",
        null=True,
        blank=True,
    )
    slug = models.CharField(
        max_length=100,
        verbose_name="Слаг текстового блока",
        help_text="Максимум 100 символов, для привязки к событию на беке",
        unique=True,
    )
    lk_type: str = models.CharField(
        verbose_name="Сервис ЛК, в котором применяется текстовый блок",
        choices=LkType.choices,
        max_length=10,
        help_text="Не участвует в бизнес-логике, поле для фильтрации в админке",
    )
    description = models.TextField(
        verbose_name="Описание назначения текстового блока",
        null=True,
        blank=True,
        help_text="Не участвует в бизнес-логике, поле для доп. описания",
    )

    created_at = models.DateTimeField(verbose_name="Когда создано", help_text="Когда создано", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Когда обновлено", help_text="Когда обновлено", auto_now=True)

    def __str__(self) -> str:
        return self.slug

    class Meta:
        db_table = "text_block_text_block"
        verbose_name = "Текстовый блок"
        verbose_name_plural = "Текстовые блоки"
