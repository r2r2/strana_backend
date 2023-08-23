from django.db import models


class AgencyGeneralType(models.Model):
    """
    Таблица типа агентства (агрегатор/АН).
    """

    sort = models.IntegerField(verbose_name='Сортировка', default=0)
    slug = models.CharField(verbose_name='Слаг', max_length=20, unique=True)
    label = models.CharField(verbose_name='Название типа', max_length=40)

    def __str__(self):
        return self.label

    class Meta:
        managed = False
        db_table = "agencies_agency_general_type"
        ordering = ("sort",)
        verbose_name = "Тип агентств"
        verbose_name_plural = "2.11. [Справочник] Типы агентств"

