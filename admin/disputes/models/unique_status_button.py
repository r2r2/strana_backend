from django.db import models


class UniqueStatusButton(models.Model):
    """
    Кнопка статуса уникальности
    """
    text = models.CharField(
        verbose_name="Текст",
        max_length=255,
        blank=True,
        null=True,
    )
    slug = models.CharField(
        verbose_name="Слаг",
        max_length=255,
        blank=True,
        null=True,
    )
    background_color = models.CharField(
        verbose_name="Цвет фона",
        max_length=7,
        blank=True,
        null=True,
        default="#8F00FF",
    )
    text_color = models.CharField(
        verbose_name="Цвет текста",
        max_length=7,
        blank=True,
        null=True,
        default="#FFFFFF",
    )
    description = models.TextField(
        verbose_name="Описание",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.text or self.slug or str(self.id)

    class Meta:
        managed = False
        db_table = 'users_unique_statuses_buttons'
        verbose_name = 'Кнопка для статуса уникальности'
        verbose_name_plural = '6.7. Кнопки для статусов уникальности'
