from django.db import models


class EventTag(models.Model):
    """
    Теги мероприятий.
    """

    name = models.CharField(verbose_name='Название тега', max_length=100)
    color = models.CharField(
        verbose_name='Цвет тега', max_length=40, default="#808080", help_text="HEX код цвета, например #808080"
    )
    text_color = models.CharField(
        verbose_name='Цвет текста тега', max_length=40, default="#808080", help_text="HEX код цвета, например #808080"
    )

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "event_event_tag"
        verbose_name = "Тег мероприятий"
        verbose_name_plural = "8.2. [Справочник] Теги мероприятий"
