from django.db import models


class AdditionalServiceGroupStatus(models.Model):
    """
    Модель группирующих статусов для доп услуг
    """

    name: str = models.CharField(
        max_length=150, verbose_name="Название группирующего статуса", null=True
    )
    slug: str = models.CharField(
        max_length=50, verbose_name="slug", null=True, unique=True
    )
    sort: int = models.IntegerField(verbose_name="Сортировка", default=0)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "additional_services_group_statuses"
        verbose_name = "группирующий статус"
        verbose_name_plural = "1.11. [Доп. услуги] Группирующие статусы"
        ordering = ["sort"]
