from django.db import models


class MeetingStatus(models.Model):
    """
    Таблица статусов встреч.
    """

    sort = models.IntegerField(verbose_name='Сортировка', default=0)
    slug = models.CharField(verbose_name='Слаг', max_length=20, unique=True)
    label = models.CharField(verbose_name='Название статуса встречи', max_length=40)
    is_final = models.BooleanField(verbose_name='Завершающий статус', default=False)

    def __str__(self):
        return self.slug

    class Meta:
        managed = False
        db_table = "meetings_status_meeting"
        ordering = ("sort",)
        verbose_name = "Статус встречи"
        verbose_name_plural = "8.5. [Справочник] Статусы встреч"

