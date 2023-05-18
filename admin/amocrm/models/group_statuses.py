from django.db import models


class AmocrmGroupStatus(models.Model):
    """
    Таблица группирующих статусов из AmoCRM
    """

    sort = models.IntegerField(verbose_name='Сортировка', default=0)
    name = models.CharField(verbose_name='Название статуса', max_length=150)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "amocrm_group_statuses"
        ordering = ("sort",)
        verbose_name = "Группирующий статус"
        verbose_name_plural = "Группирующие статусы"
